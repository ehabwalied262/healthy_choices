from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import log_message, update_user, get_user_state
from advice import TOPICS
from advice import WELCOME_MESSAGE, USAGE_TEXT, ADVICE
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
import google.generativeai as genai  # Ensure this is imported for Gemini API
from database import get_request_count, increment_request_count
import asyncio

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
    
    # ملاحظة: في handle_topic_selection، هنحذف topics_message و instruction_message باستخدام
    # await client.delete_messages(user_id, [topics_message.id, instruction_message.id])

import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
import google.generativeai as genai
from database import get_request_count, increment_request_count

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
            "آسف يا نجم، حصل مشكلة صغيرة! 😅 جرب تاني أو قولي عايز إيه بالظبط!"
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