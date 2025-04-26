from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import log_message, update_user, get_user_state
from advice import TOPICS
from advice import WELCOME_MESSAGE, USAGE_TEXT, ADVICE
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
import google.generativeai as genai  # Ensure this is imported for Gemini API
from database import get_request_count, increment_request_count
import asyncio
import json

# Handler for /start command
async def handle_start(client, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    print(f"Received /start from user {user_id}")
    update_user(user_id, username)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("وريني هنتكلم علي ايه", callback_data="show_topics")]
    ])
    await message.reply_text(WELCOME_MESSAGE, reply_markup=keyboard)
    log_message(user_id, message.text)

# Handler for /my_nutritionist command
async def handle_my_nutritionist(client, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    print(f"Received /my_nutritionist from user {user_id}")
    update_user(user_id, username)
    
    # تعريف عثفور
    intro_message = (
        "أهلاً يا جميل! 🌟 أنا عثفور، طبيب وأخصائي تغذية بشتغل على نفسي عشان أساعدك بأحسن طريقة. "
        "طبعًا الكمال لله وحده، فأكيد ممكن أعمل أخطاء، بس أنا بتعلم كل يوم عشان أقلل الغلط وأبقى أحسن. "
        "دلوقتي أنا عايز أسألك كام سؤال صغير عشان أعرف أديلك نصايح مخصصة تناسبك بالظبط، مش نصايح عامة. جاهز؟"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("أكيد، يلا نبدأ!", callback_data="nutritionist_start")]
    ])
    await message.reply_text(intro_message, reply_markup=keyboard)
    log_message(user_id, message.text)

# Handler for starting the nutritionist questions
async def handle_nutritionist_start(client, callback_query):
    user_id = callback_query.from_user.id
    
    print(f"Starting nutritionist questions for user {user_id}")
    
    # السؤال الأول: هل عندك أمراض مزمنة؟
    question = "عندك أي أمراض مزمنة زي السكر، الضغط، أو مشاكل في القلب؟ لو أيوه، إيه بالظبط؟"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("أيوه", callback_data="nutritionist_has_condition_yes")],
        [InlineKeyboardButton("لأ", callback_data="nutritionist_has_condition_no")]
    ])
    await callback_query.message.edit_text(question, reply_markup=keyboard)
    log_message(user_id, "Started nutritionist questions")

# Handler for handling the "has condition" response
async def handle_nutritionist_has_condition(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    if data == "nutritionist_has_condition_yes":
        # سؤال ثاني: إيه المرض؟
        question = "تمام، إيه المرض اللي عندك؟"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("سكر", callback_data="nutritionist_condition_diabetes")],
            [InlineKeyboardButton("ضغط", callback_data="nutritionist_condition_hypertension")],
            [InlineKeyboardButton("مشكلة في القلب", callback_data="nutritionist_condition_heart")]
        ])
        await callback_query.message.edit_text(question, reply_markup=keyboard)
        update_user(user_id, callback_query.from_user.username or "Unknown", has_condition="yes")
    elif data == "nutritionist_has_condition_no":
        # السؤال التالي: كام وزنك وطولك؟
        question = "كام وزنك وطولك؟ (اكتبلي مثلاً: 70 كيلو و 175 سم)"
        await callback_query.message.edit_text(question)
        update_user(user_id, callback_query.from_user.username or "Unknown", has_condition="no")
    log_message(user_id, f"Has condition response: {data}")

# Handler for /my_nutritionist command
async def handle_my_nutritionist(client, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    print(f"Received /my_nutritionist from user {user_id}")
    # تحديث بيانات المستخدم بدون مفاتيح إضافية في الوقت الحالي
    update_user(user_id, username)
    
    # تعريف عثفور
    intro_message = (
        "أهلاً يا نجم! 🌟 أنا عثفور، طبيب وأخصائي تغذية بشتغل على نفسي عشان أساعدك بأحسن طريقة. "
        "طبعًا الكمال لله وحده، فأكيد ممكن أعمل أخطاء، بس أنا بتعلم كل يوم عشان أقلل الغلط وأبقى أحسن. "
        "دلوقتي أنا عايز أسألك كام سؤال صغير عشان أعرف أديلك نصايح مخصصة تناسبك بالظبط، مش نصايح عامة. جاهز؟"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("أكيد، يلا نبدأ!", callback_data="nutritionist_start")]
    ])
    await message.reply_text(intro_message, reply_markup=keyboard)
    log_message(user_id, message.text)

# Handler for starting the nutritionist questions
async def handle_nutritionist_start(client, callback_query):
    user_id = callback_query.from_user.id
    
    print(f"Starting nutritionist questions for user {user_id}")
    
    # السؤال الأول: هل عندك أمراض مزمنة؟
    question = "عندك أي أمراض مزمنة زي السكر، الضغط، أو مشاكل في القلب؟ لو أيوه، إيه بالظبط؟"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("أيوه", callback_data="nutritionist_has_condition_yes")],
        [InlineKeyboardButton("لأ", callback_data="nutritionist_has_condition_no")]
    ])
    await callback_query.message.edit_text(question, reply_markup=keyboard)
    log_message(user_id, "Started nutritionist questions")

# Handler for handling the "has condition" response
async def handle_nutritionist_has_condition(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    # تحديث بيانات المستخدم مع إضافة الحالة الصحية
    if data == "nutritionist_has_condition_yes":
        question = "تمام، إيه المرض اللي عندك؟"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("سكر", callback_data="nutritionist_condition_diabetes")],
            [InlineKeyboardButton("ضغط", callback_data="nutritionist_condition_hypertension")],
            [InlineKeyboardButton("مشكلة في القلب", callback_data="nutritionist_condition_heart")]
        ])
        await callback_query.message.edit_text(question, reply_markup=keyboard)
        update_user(user_id, callback_query.from_user.username or "Unknown", has_condition="yes")
    elif data == "nutritionist_has_condition_no":
        question = "كام وزنك وطولك؟ (اكتبلي مثلاً: 70 كيلو و 175 سم)"
        await callback_query.message.edit_text(question)
        update_user(user_id, callback_query.from_user.username or "Unknown", has_condition="no")
    log_message(user_id, f"Has condition response: {data}")

# Handler for handling the condition type response
async def handle_nutritionist_condition(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    condition = ""
    if data == "nutritionist_condition_diabetes":
        condition = "سكر"
    elif data == "nutritionist_condition_hypertension":
        condition = "ضغط"
    elif data == "nutritionist_condition_heart":
        condition = "مشكلة في القلب"
    
    update_user(user_id, callback_query.from_user.username or "Unknown", condition=condition)
    
    # السؤال التالي: كام وزنك وطولك؟
    question = "كام وزنك وطولك؟ (اكتبلي مثلاً: 70 كيلو و 175 سم)"
    await callback_query.message.edit_text(question)
    log_message(user_id, f"Condition selected: {condition}")

# Handler for handling text input (weight and height, meals, activity, restrictions)
async def handle_nutritionist_text_input(client, message: Message):
    user_id = message.from_user.id
    user_state = get_user_state(user_id)
    text = message.text
    
    # استخدام Gemini لفهم إجابات المستخدم
    model = genai.GenerativeModel('gemini-1.5-flash-002')
    
    # السؤال الأول: كام وزنك وطولك؟
    if "weight" not in user_state or "height" not in user_state:
        try:
            prompt = (
                f"المستخدم كتب: '{text}'.\n"
                "أنا سألته: 'كام وزنك وطولك؟ (اكتبلي مثلاً: 70 كيلو و 175 سم)'.\n"
                "استخرجلي الوزن والطول من إجابته، ولو فيه وحدات زي 'كيلو' أو 'ك' أو 'سم'، احذفها. "
                "رجعلي الإجابة بصيغة JSON كده:\n"
                "{\n"
                "  \"weight\": \"رقم الوزن\",\n"
                "  \"height\": \"رقم الطول\"\n"
                "}\n"
                "لو ما قدرتش تفهم الإجابة، رجعلي:\n"
                "{\n"
                "  \"error\": \"مش فاهم الإجابة\"\n"
                "}"
            )
            response = await asyncio.to_thread(model.generate_content, prompt)
            gemini_response = response.text
            
            # تنظيف الرد من ```json ... ```
            gemini_response = gemini_response.strip()
            if gemini_response.startswith("```json") and gemini_response.endswith("```"):
                gemini_response = gemini_response[7:-3].strip()
            
            # تحويل الرد لـ JSON
            try:
                result = json.loads(gemini_response)
            except json.JSONDecodeError as e:
                print(f"Error parsing Gemini response as JSON: {e}, response: {gemini_response}")
                # استخدام Gemini لتوضيح الخطأ
                error_prompt = (
                    f"المستخدم كتب: '{text}'.\n"
                    "أنا سألته: 'كام وزنك وطولك؟ (اكتبلي مثلاً: 70 كيلو و 175 سم)'.\n"
                    "ما فهمتش إجابته. رد عليا بجملة باللهجة المصرية الودودة توضح إني مش فاهم إجابته، "
                    "وقول للمستخدم هو مش فاهم إيه بالظبط، واديله مثال مناسب للسؤال."
                )
                error_response = await asyncio.to_thread(model.generate_content, error_prompt)
                await message.reply_text(error_response.text)
                return
            
            if "error" in result:
                # استخدام Gemini لتوضيح الخطأ
                error_prompt = (
                    f"المستخدم كتب: '{text}'.\n"
                    "أنا سألته: 'كام وزنك وطولك؟ (اكتبلي مثلاً: 70 كيلو و 175 سم)'.\n"
                    "ما فهمتش إجابته. رد عليا بجملة باللهجة المصرية الودودة توضح إني مش فاهم إجابته، "
                    "وقول للمستخدم هو مش فاهم إيه بالظبط، واديله مثال مناسب للسؤال."
                )
                error_response = await asyncio.to_thread(model.generate_content, error_prompt)
                await message.reply_text(error_response.text)
                return
            
            weight = result.get("weight")
            height = result.get("height")
            
            if not weight.isdigit() or not height.isdigit():
                print(f"Invalid weight or height extracted: weight={weight}, height={height}")
                error_prompt = (
                    f"المستخدم كتب: '{text}'.\n"
                    "أنا سألته: 'كام وزنك وطولك؟ (اكتبلي مثلاً: 70 كيلو و 175 سم)'.\n"
                    "ما فهمتش إجابته لأن الأرقام مش واضحة. رد عليا بجملة باللهجة المصرية الودودة توضح إني مش فاهم إجابته، "
                    "وقول للمستخدم هو مش فاهم إيه بالظبط، واديله مثال مناسب للسؤال."
                )
                error_response = await asyncio.to_thread(model.generate_content, error_prompt)
                await message.reply_text(error_response.text)
                return
            
            update_user(user_id, message.from_user.username or "Unknown", weight=weight, height=height)
            
            # السؤال التالي: كام وجبة بتاكلها في اليوم؟
            question = "بتاكل كام وجبة في اليوم؟ وإيه أكتر حاجة بتحب تاكلها (مثلاً لحوم، خضار، حلويات)؟"
            await message.reply_text(question)
        except Exception as e:
            print(f"Error processing weight/height with Gemini for user {user_id}: {e}")
            await message.reply_text("معلش، حصل خطأ! جرب تاني ولو المشكلة تكررت قوللي.")
    
    # السؤال التالي: العادات الغذائية
    elif "meals_per_day" not in user_state:
        try:
            prompt = (
                f"المستخدم كتب: '{text}'.\n"
                "أنا سألته: 'بتاكل كام وجبة في اليوم؟ وإيه أكتر حاجة بتحب تاكلها (مثلاً لحوم، خضار، حلويات)؟'.\n"
                "استخرجلي عدد الوجبات والأكل المفضل من إجابته. لو الإجابة مش واضحة، حاول تفهمها بشكل طبيعي. "
                "مثلاً لو قال '3 وجبات وأحب الدجاج' أو 'بفطر وبس وبحب الحلويات'، افهم إن ده وجبة واحدة. "
                "رجعلي الإجابة بصيغة JSON كده:\n"
                "{\n"
                "  \"meals_per_day\": \"عدد الوجبات (رقم أو نص)\",\n"
                "  \"favorite_food\": \"نوع الأكل المفضل\"\n"
                "}\n"
                "لو ما قدرتش تفهم الإجابة، رجعلي:\n"
                "{\n"
                "  \"error\": \"مش فاهم الإجابة\"\n"
                "}"
            )
            response = await asyncio.to_thread(model.generate_content, prompt)
            gemini_response = response.text
            
            # تنظيف الرد من ```json ... ```
            gemini_response = gemini_response.strip()
            if gemini_response.startswith("```json") and gemini_response.endswith("```"):
                gemini_response = gemini_response[7:-3].strip()
            
            # تحويل الرد لـ JSON
            try:
                result = json.loads(gemini_response)
            except json.JSONDecodeError as e:
                print(f"Error parsing Gemini response as JSON: {e}, response: {gemini_response}")
                error_prompt = (
                    f"المستخدم كتب: '{text}'.\n"
                    "أنا سألته: 'بتاكل كام وجبة في اليوم؟ وإيه أكتر حاجة بتحب تاكلها (مثلاً لحوم، خضار، حلويات)؟'.\n"
                    "ما فهمتش إجابته. رد عليا بجملة باللهجة المصرية الودودة توضح إني مش فاهم إجابته، "
                    "وقول للمستخدم هو مش فاهم إيه بالظبط، واديله مثال مناسب للسؤال."
                )
                error_response = await asyncio.to_thread(model.generate_content, error_prompt)
                await message.reply_text(error_response.text)
                return
            
            if "error" in result:
                error_prompt = (
                    f"المستخدم كتب: '{text}'.\n"
                    "أنا سألته: 'بتاكل كام وجبة في اليوم؟ وإيه أكتر حاجة بتحب تاكلها (مثلاً لحوم، خضار، حلويات)؟'.\n"
                    "ما فهمتش إجابته. رد عليا بجملة باللهجة المصرية الودودة توضح إني مش فاهم إجابته، "
                    "وقول للمستخدم هو مش فاهم إيه بالظبط، واديله مثال مناسب للسؤال."
                )
                error_response = await asyncio.to_thread(model.generate_content, error_prompt)
                await message.reply_text(error_response.text)
                return
            
            meals_per_day = result.get("meals_per_day")
            favorite_food = result.get("favorite_food")
            
            update_user(user_id, message.from_user.username or "Unknown", meals_per_day=meals_per_day, favorite_food=favorite_food)
            
            # السؤال التالي: مستوى النشاط البدني
            question = "بتمارس رياضة أو بتمشي كتير؟ لو أيوه، كام مرة في الأسبوع وب تعمل إيه بالظبط؟"
            await message.reply_text(question)
        except Exception as e:
            print(f"Error processing meals/favorite food with Gemini for user {user_id}: {e}")
            await message.reply_text("معلش، حصل خطأ! جرب تاني ولو المشكلة تكررت قوللي.")
    
    # السؤال التالي: النشاط البدني
    elif "activity_level" not in user_state:
        try:
            prompt = (
                f"المستخدم كتب: '{text}'.\n"
                "أنا سألته: 'بتمارس رياضة أو بتمشي كتير؟ لو أيوه، كام مرة في الأسبوع وب تعمل إيه بالظبط؟'.\n"
                "استخرجلي مستوى النشاط البدني من إجابته. "
                "لو قال 'لأ' أو 'مش بمارس رياضة' أو 'مش بعمل حاجة'، افهم إنه مش بيمارس أي نشاط وخلّي الإجابة 'مش بمارس رياضة'. "
                "لو قال 'أيوه'، لازم يقول كام مرة وإيه الرياضة، مثلاً 'أيوه، 3 مرات أجري' أو 'بمشي كل يوم'. "
                "رجعلي الإجابة بصيغة JSON كده:\n"
                "{\n"
                "  \"activity_level\": \"وصف مستوى النشاط (نص)\"\n"
                "}\n"
                "لو ما قدرتش تفهم الإجابة، رجعلي:\n"
                "{\n"
                "  \"error\": \"مش فاهم الإجابة\"\n"
                "}"
            )
            response = await asyncio.to_thread(model.generate_content, prompt)
            gemini_response = response.text
            
            # تنظيف الرد من ```json ... ```
            gemini_response = gemini_response.strip()
            if gemini_response.startswith("```json") and gemini_response.endswith("```"):
                gemini_response = gemini_response[7:-3].strip()
            
            # تحويل الرد لـ JSON
            try:
                result = json.loads(gemini_response)
            except json.JSONDecodeError as e:
                print(f"Error parsing Gemini response as JSON: {e}, response: {gemini_response}")
                error_prompt = (
                    f"المستخدم كتب: '{text}'.\n"
                    "أنا سألته: 'بتمارس رياضة أو بتمشي كتير؟ لو أيوه، كام مرة في الأسبوع وب تعمل إيه بالظبط؟'.\n"
                    "ما فهمتش إجابته. رد عليا بجملة باللهجة المصرية الودودة توضح إني مش فاهم إجابته، "
                    "وقول للمستخدم هو مش فاهم إيه بالظبط، واديله مثال مناسب للسؤال."
                )
                error_response = await asyncio.to_thread(model.generate_content, error_prompt)
                await message.reply_text(error_response.text)
                return
            
            if "error" in result:
                error_prompt = (
                    f"المستخدم كتب: '{text}'.\n"
                    "أنا سألته: 'بتمارس رياضة أو بتمشي كتير؟ لو أيوه، كام مرة في الأسبوع وب تعمل إيه بالظبط؟'.\n"
                    "ما فهمتش إجابته. رد عليا بجملة باللهجة المصرية الودودة توضح إني مش فاهم إجابته، "
                    "وقول للمستخدم هو مش فاهم إيه بالظبط، واديله مثال مناسب للسؤال."
                )
                error_response = await asyncio.to_thread(model.generate_content, error_prompt)
                await message.reply_text(error_response.text)
                return
            
            activity_level = result.get("activity_level")
            
            update_user(user_id, message.from_user.username or "Unknown", activity_level=activity_level)
            
            # السؤال التالي: الأهداف الصحية
            question = "إيه هدفك دلوقتي؟ عايز تنقّص وزن، تزوّد عضل، ولا بس تحافظ على صحتك؟"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("أنقّص وزن", callback_data="nutritionist_goal_weight_loss")],
                [InlineKeyboardButton("أزوّد عضل", callback_data="nutritionist_goal_muscle_gain")],
                [InlineKeyboardButton("أحافظ على صحتي", callback_data="nutritionist_goal_maintain_health")]
            ])
            await message.reply_text(question, reply_markup=keyboard)
        except Exception as e:
            print(f"Error processing activity level with Gemini for user {user_id}: {e}")
            await message.reply_text("معلش، حصل خطأ! جرب تاني ولو المشكلة تكررت قوللي.")
            
# Handler for handling the health goal response
async def handle_nutritionist_goal(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    goal = ""
    if data == "nutritionist_goal_weight_loss":
        goal = "إنقاص الوزن"
    elif data == "nutritionist_goal_muscle_gain":
        goal = "زيادة العضل"
    elif data == "nutritionist_goal_maintain_health":
        goal = "الحفاظ على الصحة"
    
    update_user(user_id, callback_query.from_user.username or "Unknown", goal=goal)
    
    # السؤال التالي: الحساسية الغذائية
    question = "عندك أي حساسية من أكل معين؟ ولا فيه أكل مش بتحبه أو ما بتاكلوش (زي اللحوم أو الألبان)؟"
    await callback_query.message.edit_text(question)
    log_message(user_id, f"Goal selected: {goal}")

# Handler for handling the food restrictions response
async def handle_food_restrictions(client, message: Message):
    user_id = message.from_user.id
    text = message.text
    
    # استخدام Gemini لفهم الحساسيات أو القيود الغذائية
    model = genai.GenerativeModel('gemini-1.5-flash-002')
    try:
        prompt = (
            f"المستخدم كتب: '{text}'.\n"
            "أنا سألته: 'عندك أي حساسية من أكل معين؟ ولا فيه أكل مش بتحبه أو ما بتاكلوش (زي اللحوم أو الألبان)؟'.\n"
            "استخرجلي الحساسيات أو القيود الغذائية من إجابته. "
            "رجعلي الإجابة بصيغة JSON كده:\n"
            "{\n"
            "  \"food_restrictions\": \"وصف الحساسيات أو القيود (نص)\"\n"
            "}\n"
            "لو ما قدرتش تفهم الإجابة، رجعلي:\n"
            "{\n"
            "  \"error\": \"مش فاهم الإجابة\"\n"
            "}"
        )
        response = await asyncio.to_thread(model.generate_content, prompt)
        gemini_response = response.text
        
        # تنظيف الرد من ```json ... ```
        gemini_response = gemini_response.strip()
        if gemini_response.startswith("```json") and gemini_response.endswith("```"):
            gemini_response = gemini_response[7:-3].strip()
        
        # تحويل الرد لـ JSON
        try:
            result = json.loads(gemini_response)
        except json.JSONDecodeError as e:
            print(f"Error parsing Gemini response as JSON: {e}, response: {gemini_response}")
            await message.reply_text("معلش، مش فاهم إجابتك! جرب تكتب زي كده: عندي حساسية من الألبان أو مش بحب اللحوم")
            return
        
        if "error" in result:
            await message.reply_text("معلش، مش فاهم إجابتك! جرب تكتب زي كده: عندي حساسية من الألبان أو مش بحب اللحوم")
            return
        
        food_restrictions = result.get("food_restrictions")
        
        update_user(user_id, message.from_user.username or "Unknown", food_restrictions=food_restrictions)
        
        # رسالة نهائية: خلّصنا الأسئلة
        response = (
            "كده خلّصنا الأسئلة يا نجم! 🌟 دلوقتي أنا عارف عنك حاجات كتير وهقدر أديلك نصايح مخصصة. "
            "لو عايز تشوف المعلومات اللي عرفناها عنك، استخدم الأمر /my_info. "
            "ولو عايز نبدأ نصايح مخصصة، اكتب /start_lesson."
        )
        await message.reply_text(response)
        log_message(user_id, f"Food restrictions: {food_restrictions}")
    except Exception as e:
        print(f"Error processing food restrictions with Gemini for user {user_id}: {e}")
        await message.reply_text("معلش، مش فاهم إجابتك! جرب تكتب زي كده: عندي حساسية من الألبان أو مش بحب اللحوم")

# Handler for /my_info command
async def handle_my_info(client, message: Message):
    user_id = message.from_user.id
    
    print(f"Received /my_info from user {user_id}")
    user_state = get_user_state(user_id)
    
    # جمع المعلومات اللي عرفناها عن المستخدم
    info = "معلوماتك اللي عرفناها لحد دلوقتي:\n\n"
    info += f"اسمك: {user_state.get('username', 'غير معروف')}\n"
    info += f"عندك أمراض مزمنة؟: {user_state.get('has_condition', 'غير معروف')}\n"
    if user_state.get('has_condition') == "yes":
        info += f"نوع المرض: {user_state.get('condition', 'غير معروف')}\n"
    info += f"وزنك: {user_state.get('weight', 'غير معروف')} كيلو\n"
    info += f"طولك: {user_state.get('height', 'غير معروف')} سم\n"
    info += f"عدد وجباتك في اليوم: {user_state.get('meals_per_day', 'غير معروف')}\n"
    info += f"مستوى نشاطك: {user_state.get('activity_level', 'غير معروف')}\n"
    info += f"هدفك الصحي: {user_state.get('goal', 'غير معروف')}\n"
    info += f"حساسيات أو قيود غذائية: {user_state.get('food_restrictions', 'غير معروف')}\n"
    
    await message.reply_text(info)
    log_message(user_id, message.text)

# Handler for /help command
async def handle_help(client, message: Message):
    user_id = message.from_user.id
    
    print(f"Received /help from user {user_id}")
    help_message = (
        "أهلاً يا جميل! 🌟 أنا هنا عشان أساعدك تحافظ على صحتك وتغذيتك بطريقة سهلة وممتعة. إزاي تستخدمني؟\n\n"
        "1. لو أول مرة تكلمني، اكتب /start عشان نبدأ من الأول.\n"
        "2. لو عايز تشوف المواضيع اللي نقدر نتكلم فيها، اكتب /list.\n"
        "3. لو عايز نصايح مخصصة ليك، اكتب /my_nutritionist وأنا هسألك كام سؤال عشان أظبط النصايح ليك.\n"
        "4. لو عايز تشوف المعلومات اللي عرفناها عنك، اكتب /my_info.\n"
        "5. لو مش عارف إيه الأوامر اللي تقدر تستخدمها، اكتب /menu وأنا هوريك كل حاجة!\n\n"
        "أي سؤال تاني، اكتبلي وأنا هرد عليك على طول! 😊"
    )
    await message.reply_text(help_message)
    log_message(user_id, message.text)

# Handler for /about command
async def handle_about(client, message: Message):
    user_id = message.from_user.id
    
    print(f"Received /about from user {user_id}")
    about_message = (
        "أهلاً يا جميل! 🌟 أنا عثفور، طبيب وأخصائي تغذية افتراضي، وهدفي إني أساعدك تحافظ على صحتك وتغذيتك بطريقة بسيطة وممتعة. "
        "أنا مدرب على كتب ومصادر طبية موثوقة، وبحب أشارك معاك نصايح صحية مبنية على علم، سواء عن التغذية، الرياضة، أو الوقاية من الأمراض. "
        "طبعًا الكمال لله وحده، فممكن أغلط أحيانًا، بس أنا بتعلم كل يوم عشان أبقى أحسن وأقلل أي أخطاء. "
        "لو عايز تعرفني أكتر أو تبدأ رحلتك معايا، جرب تكتب /start أو /my_nutritionist! 💪"
    )
    await message.reply_text(about_message)
    log_message(user_id, message.text)

# Handler for /menu command
async def handle_menu(client, message: Message):
    user_id = message.from_user.id
    
    print(f"Received /menu from user {user_id}")
    menu_message = (
        "أهلاً يا جميل! 🌟 دي كل الأوامر اللي تقدر تستخدمها معايا:\n\n"
        "/start - ابدأ معايا من الأول يا جميل! 🌟\n"
        "/list - شوف كل المواضيع اللي نقدر نتكلم فيها 📋\n"
        "/help - عايز تعرف إزاي تستخدمني؟ أنا هقولك! 😊\n"
        "/about - مين أنا وإيه قصتي؟ تعرف عليا أكتر! 🩺\n"
        "/my_nutritionist - عايز نصايح مخصصة ليك؟ عثفور هيسألك ويظبطلك كل حاجة! 💪\n"
        "/my_info - عايز تشوف كل المعلومات اللي عرفناها عنك؟ خش هنا! ℹ️\n"
        "/menu - مش عارف إيه الأوامر؟ أنا هوريك كل حاجة هنا! 📜\n\n"
        "اختار اللي يناسبك ويلا نبدأ! 😊"
    )
    await message.reply_text(menu_message)
    log_message(user_id, message.text)

async def handle_show_topics(client, callback_query):
    user_id = callback_query.from_user.id
    
    print(f"Received show_topics callback from user {user_id}")
    welcome_text = callback_query.message.text
    await callback_query.message.edit_text(welcome_text)  # الرسالة الأصلية تبقى زي ما هي
    
    # 1. إرسال USAGE_TEXT أولاً (دي هتفضل موجودة)
    await client.send_message(user_id, USAGE_TEXT)
    
    # 2. إنشاء وإرسال قائمة الزراير من TOPICS وحفظ الرسالة
    buttons = [
        [InlineKeyboardButton(f"{emoji} {topic}", callback_data=f"topic_{topic}")]
        for topic, emoji in TOPICS.items()
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    topics_message = await client.send_message(user_id, "اختار موضوع:", reply_markup=keyboard)  # حفظ الرسالة للحذف لاحقًا
    
    # 3. إرسال الرسالة التوجيهية وحفظها
    instruction_message = await client.send_message(
        user_id,
        "الأمراض اللي بنشتغل على الوقاية منها:\nاختار موضوع من الزراير فوق 👆"
    )
    log_message(user_id, "Clicked 'show_topics'")

async def handle_general_message(client, message):
    # Indicate typing status
    await client.send_chat_action(message.chat.id, action=ChatAction.TYPING)

    user_message = message.text
    if not user_message:
        return

    print(f"Received message from user: {user_message}")
    user_id = message.from_user.id

    try:
        # Send immediate friendly response using gemini-1.5-flash-002
        quick_model = genai.GenerativeModel('gemini-1.5-flash-002')
        quick_prompt = (
            f"رد بجملة قصيرة وودودة باللهجة المصرية تخلي المستخدم يحس إنك مهتم بسؤاله وهتفكر فيه، "
            f"وخلي الرد مختلف عن كل مرة بناءً على السؤال: '{user_message}'"
        )
        quick_response = quick_model.generate_content(quick_prompt).text
        await message.reply_text(quick_response)
        print(f"Sent quick response to user {user_id}: {quick_response}")

        # Check medical terms
        medical_terms = ["مريض سكر", "diabetes", "ضغط", "hypertension", "قلب", "heart"]
        is_medical = any(term in user_message.lower() for term in medical_terms)

        # Choose model based on request count
        request_count = get_request_count()
        model_name = 'gemini-1.5-pro-002' if request_count < 48 else 'gemini-2.5-flash'
        print(f"Using model: {model_name}, request count: {request_count}")

        try:
            # Try primary model
            model = genai.GenerativeModel(model_name)
            main_prompt = (
                f"رد على السؤال ده: '{user_message}' باللهجة المصرية الودودة. "
                f"خلي الرد واضح ومفيد ويعبر عن اهتمامك بالمستخدم. "
                f"لو السؤال طبي (زي عن السكر أو الضغط)، أضف تحذير إنك مش دكتور وإنه لازم يستشير دكتور مختص، "
                f"واقترح خيارات زي نظام غذائي صحي، فطار مناسب، أو أسئلة لتخصيص النصايح."
            )
            response = await asyncio.to_thread(model.generate_content, main_prompt)
            gemini_response = response.text

            # Add proactive suggestions for medical queries
            if is_medical:
                gemini_response += (
                    "\n\nلو عايز، أقدر أساعدك بكام حاجة زي:\n"
                    "- اقترحلك أكل صحي يناسب مرضى السكر؟\n"
                    "- أقولك على فطار لذيذ وصحي؟\n"
                    "- ولا أسألك كام سؤال عشان أعرف أديلك نصايح مخصصة؟\n"
                    "قولي إنت عايز إيه وأنا جاهز!"
                )
                update_user_state(user_id, "awaiting_medical_choice")

        except Exception as primary_error:
            print(f"Primary model {model_name} failed: {primary_error}")
            # Fallback to gemini-1.5-flash-002
            try:
                model = genai.GenerativeModel('gemini-1.5-flash-002')
                main_prompt = (
                    f"رد على السؤال ده: '{user_message}' باللهجة المصرية الودودة. "
                    f"خلي الرد بسيط ومفيد. لو السؤال طبي، أضف تحذير إنك مش دكتور."
                )
                response = await asyncio.to_thread(model.generate_content, main_prompt)
                gemini_response = response.text
                print(f"Fallback to gemini-1.5-flash-002 succeeded")
            except Exception as fallback_error:
                print(f"Fallback model failed: {fallback_error}")
                gemini_response = (
                    "معلش، حصل مشكلة تقنية بس أنا موجود! 😅 "
                    "جرب اسألني سؤال تاني أو قولي عايز مساعدة في إيه!"
                )

        # Send the main response
        await message.reply_text(gemini_response)
        print(f"Sent Gemini response to user {user_id}: {gemini_response}")

        # Increment request count if using gemini-1.5-pro-002
        if model_name == 'gemini-1.5-pro-002':
            increment_request_count()

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        await message.reply_text(
            "آسف يا جميل، حصل مشكلة صغيرة! 😅 جرب تاني أو قولي عايز إيه بالظبط!"
        )

async def handle_topic_selection(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data

    if data.startswith("topic_"):
        selected_topic = data.replace("topic_", "")
        print(f"User {user_id} selected topic: {selected_topic}")

        # Attempt to delete the button message (the one the user clicked) and the next message
        try:
            # Delete the message with the buttons
            await client.delete_messages(user_id, [callback_query.message.id])

            # Optionally, delete the next message if it exists and was sent by the bot
            try:
                next_message_id = callback_query.message.id + 1
                next_message = await client.get_messages(user_id, next_message_id)
                if next_message.from_user.is_bot:  # Ensure the next message was sent by the bot
                    await client.delete_messages(user_id, [next_message_id])
            except Exception as e:
                # Handle cases where the next message doesn't exist or can't be deleted
                print(f"Failed to delete next message: {e}")
        except pyrogram.errors.MessageDeleteForbidden:
            # Handle cases where the bot doesn't have permission to delete the message
            print(f"Bot does not have permission to delete message {callback_query.message.id} in chat {user_id}")
        
        # Start the intro
        intro_list = ADVICE[selected_topic]["intro"]
        update_user(user_id, callback_query.from_user.username or "Unknown", current_topic=selected_topic, advice_index=0, intro_index=0)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("التالي", callback_data=f"intro_{selected_topic}_0")]
        ])
        await client.send_message(user_id, intro_list[0], reply_markup=keyboard)
        log_message(user_id, f"Selected topic: {selected_topic}")

# Handler for intro and advice navigation
async def handle_next_advice(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data.split("_")
    
    # طباعة الـ callback_data للتشخيص
    print(f"Callback data: {callback_query.data}, Split data: {data}")
    
    # التأكد إن الـ data فيها على الأقل prefix و topic و index
    if len(data) < 3:
        await client.send_message(user_id, "فيه مشكلة في الزرار، جرب تاني!")
        print(f"Error: Invalid callback data format: {callback_query.data}")
        return
    
    # تحديد الـ prefix
    prefix = data[0] if data[0] == "intro" else "_".join(data[0:2])  # "intro" أو "next_advice"
    # الـ topic هيكون بعد الـ prefix
    topic_start_index = 1 if prefix == "intro" else 2
    topic = "_".join(data[topic_start_index:-1])  # لو الـ topic فيه "_" زي "عادات_الأكل"
    # الـ index دايماً آخر جزء
    try:
        current_index = int(data[-1])  # الـ index الحالي
    except (ValueError, IndexError):
        await client.send_message(user_id, "حصل خطأ في ترتيب النصوص، جرب تاني!")
        print(f"Error: Could not parse index from callback data: {callback_query.data}")
        return
    
    # إزالة الزرار من الرسالة الحالية
    await callback_query.message.edit_text(callback_query.message.text)
    
    if prefix == "intro":
        intro_list = ADVICE[topic]["intro"]
        next_index = current_index + 1
        
        print(f"User {user_id} requested next intro for {topic}, index {current_index}")
        if next_index < len(intro_list):
            # عرض الرسالة التمهيدية التالية
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("التالي", callback_data=f"intro_{topic}_{next_index}")]
            ])
            await client.send_message(user_id, intro_list[next_index], reply_markup=keyboard)
            update_user(user_id, callback_query.from_user.username or "Unknown", current_topic=topic, intro_index=next_index, advice_index=0)
        else:
            # لما الـ intro تخلّص، نروح للنصايح
            advice_list = ADVICE[topic]["tips"]
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("النصيحة اللي بعد كده", callback_data=f"next_advice_{topic}_0")]
            ])
            await client.send_message(user_id, advice_list[0], reply_markup=keyboard)
            update_user(user_id, callback_query.from_user.username or "Unknown", current_topic=topic, advice_index=0, intro_index=None)
        log_message(user_id, f"Viewed intro {next_index} for {topic}")
    
    elif prefix == "next_advice":
        advice_list = ADVICE[topic]["tips"]
        next_index = current_index + 1
        
        print(f"User {user_id} requested next advice for {topic}, index {current_index}")
        if next_index < len(advice_list):
            # عرض النصيحة التالية
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("النصيحة اللي بعد كده", callback_data=f"next_advice_{topic}_{next_index}")]
            ])
            await client.send_message(user_id, advice_list[next_index], reply_markup=keyboard)
            update_user(user_id, callback_query.from_user.username or "Unknown", current_topic=topic, advice_index=next_index, intro_index=None)
        else:
            # لما النصايح تخلّص
            await client.send_message(user_id, "كده تمام! خلّصنا النصايح. لو عايز موضوع تاني، استخدم /list.")
            update_user(user_id, callback_query.from_user.username or "Unknown", current_topic=None, advice_index=0, intro_index=None)
        log_message(user_id, f"Viewed advice {next_index} for {topic}")
    else:
        print(f"Error: Unknown prefix in callback data: {callback_query.data}")
        await client.send_message(user_id, "حصل خطأ غريب، جرب تاني!")

# Handler for /list command
async def handle_list(client, message: Message):
    user_id = message.from_user.id
    
    print(f"Received /list from user {user_id}")
    buttons = [
        [InlineKeyboardButton(f"{emoji} {topic}", callback_data=f"topic_{topic}")]
        for topic, emoji in TOPICS.items()
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await client.send_message(
        user_id,
        "المصايب بتاعتنا:\nاختار موضوع من الزراير تحت 👇",
        reply_markup=keyboard
    )
    log_message(user_id, message.text)