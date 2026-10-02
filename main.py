import asyncio
import random
from keep_alive import keep_alive
import discord
from discord.ext import commands

# إعداد الصلاحيات (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  print(f"تم تسجيل الدخول بنجاح باسم: {bot.user}")


# ==========================================
# ⚙️ 1. أوامر الإدارة (Administrative Tools)
# ==========================================


# أمر الطرد (Kick)
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
  await member.kick(reason=reason)
  await ctx.send(f"❌ تم طرد العضو {member.mention} | السبب: {reason}")


# أمر الحظر (Ban)
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
  await member.ban(reason=reason)
  await ctx.send(f"🔨 تم حظر العضو {member.mention} | السبب: {reason}")


# أمر مسح الرسائل (Clear)
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
  await ctx.channel.purge(limit=amount + 1)
  await ctx.send(f"🧹 تم مسح {amount} رسالة.", delete_after=3)


# ==========================================
# 🎲 2. لعبة الروليت (Roulette Game)
# ==========================================

roulette_players = []
roulette_active = False


@bot.command()
async def roulette(ctx):
  global roulette_active, roulette_players

  if roulette_active:
    await ctx.send("⚠️ هناك لعبة روليت قائمة بالفعل!")
    return

  roulette_active = True
  roulette_players = [ctx.author]  # منشئ اللعبة ينضم تلقائياً

  embed = discord.Embed(
      title="🎲 بدأت لعبة الروليت!",
      description=(
          f"قام {ctx.author.mention} ببدء لعبة روليت!\n\n"
          "اكتب **`انضمام`** أو **`join`** خلال **50 ثانية** للمشاركة.\n"
          "⚠️ *ملاحظة: الخاسر سيتعرض للطرد (Kick) من السيرفر!*"
      ),
      color=discord.Color.red(),
  )
  await ctx.send(embed=embed)

  # فحص الرسائل للانضمام
  def check(m):
    return (
        m.channel == ctx.channel
        and m.content.lower() in ["انضمام", "join"]
        and m.author not in roulette_players
    )

  end_time = asyncio.get_event_loop().time() + 50
  while asyncio.get_event_loop().time() < end_time:
    try:
      timeout = end_time - asyncio.get_event_loop().time()
      if timeout <= 0:
        break
      msg = await bot.wait_for("message", check=check, timeout=timeout)
      roulette_players.append(msg.author)
      await ctx.send(f"✅ انضم {msg.author.mention} إلى اللعبة!")
    except asyncio.TimeoutError:
      break

  # بدء الاقتراع بعد انتهاء الـ 50 ثانية
  if len(roulette_players) < 2:
    await ctx.send(
        "❌ تم إلغاء اللعبة لعدم وجود عدد كافٍ من اللاعبين (يلزم 2 على الأقل)."
    )
    roulette_active = False
    return

  await ctx.send(
      f"🎯 انتهى وقت الانضمام! عدد المشاركين: {len(roulette_players)}\nجاري تدوير الروليت... 🔄"
  )
  await asyncio.sleep(3)

  # اختيار خاسر عشوائي
  loser = random.choice(roulette_players)
  await ctx.send(
      f"💥 **استقرت الروليت على: {loser.mention}!**\nلديك **15 ثانية** لقراءة التعاويذ قبل الطرد! ⏱️"
  )

  await asyncio.sleep(15)

  # محاولة طرد الخاسر
  try:
    await loser.kick(reason="خسر في لعبة الروليت!")
    await ctx.send(f"👋 تم طرد {loser.mention} بنجاح!")
  except Exception as e:
    await ctx.send(
        f"⚠️ تعذر طرد {loser.mention} (ربما يملك صلاحيات أعلى من البوت)."
    )

  roulette_active = False


# ==========================================
# 🚀 تشغيل البوت
# ==========================================

keep_alive()  # تشغيل سيرفر الويب للمحافظة على الاتصال

# ضع التوكن الخاص ببوتك هنا بين التنصيص
BOT_TOKEN = "MTU0MjY0ODk2NDAxOTM5MjU1Mw.GNnugF.6W04GxqxGX3ylkLAzSMiYzEZiPDEUfHGGdbwX0"

if __name__ == "__main__":
  bot.run(BOT_TOKEN)
