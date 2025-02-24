### Config ###
import nextcord
from nextcord.ext import commands
import random
import sqlite3

import toss


config = {
    ### Discord Config ###
    "token": "MTM0MzE4MTY0NzM3MzQwMjE1NA.GcAIKR.u0WPIlZtlNVhr-gSBSnx08FLURRj4NahKHW_ro",
    "guild_id": 1343156808230899725,
    "bot_status": "로나랜드 오리지널",
    ### Toss Config ###
    "toss_token": "",
    "toss_id": ""
}

AdminList = [1251376918335455259,1339650919553437729]

def execute_query(query, params=()):
    try:
        con = sqlite3.connect('./database.db')
        cur = con.cursor()
        cur.execute(query, params)
        result = cur.fetchall()
        con.commit()
        con.close()
        return result
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None

# Toss 요청 함수
def makeTossRequest(amount):
    result = toss.request(token=config['toss_token'], toss_id=config["toss_id"], amount=amount)
    if result == 'FAIL':
        return False
    else:
        return result

# Toss 확인 함수
def getTossConfirm(code):
    result = toss.confirm(token=config["toss_token"], code=code)
    if result['result'] == 'FAIL':
        return False, result['message']
    else:
        return True, result['message']

# 사용자 존재 여부 확인
def checkUser(id):
    result = execute_query("SELECT * FROM user WHERE id == ?;", (id,))
    return bool(result)

# 사용자 데이터 생성
def makeUserData(id):
    execute_query("INSERT INTO user VALUES(?, ?, ?)", (id, 0, '0:0'))
    return True

# 임베드 메시지 생성
def makeEmbed(code, des):
    if code == 'error':
        embed = nextcord.Embed(
            title='로나랜드 오류알림',
            description=f'**```css\n[ ⛔ ] {des}```**'
        )
    return embed

# 사용자 금액 조회
def getUserMoney(id):
    result = execute_query("SELECT * FROM user WHERE id = ?;", (id,))
    return result[0][1] if result else 0

# 사용자 금액 차감
def removeUserMoney(id, money):
    last_money = getUserMoney(id)
    new_money = last_money - int(money)
    execute_query("UPDATE user SET money = ? WHERE id == ?;", (new_money, id))
    return True

# 관리자 금액 수정
def adminAddUserMoney(id, money):
    execute_query("UPDATE user SET money = ? WHERE id == ?;", (money, id))
    execute_query("UPDATE user SET roll = ? WHERE id == ?;", (f'{money}:0', id))
    return True

# 사용자 금액 추가
def addUserMoney(id, money):
    last_money = getUserMoney(id)
    new_money = last_money + int(money)
    execute_query("UPDATE user SET money = ? WHERE id == ?;", (new_money, id))
    return True

# 롤링 금액 추가
def addRolling(id, money):
    charge_money, last_money = getRolling(id)
    new_money = last_money + int(money)
    execute_query("UPDATE user SET roll = ? WHERE id == ?;", (f'{charge_money}:{new_money}', id))
    return True

# 롤링 확인
def checkRolling(id):
    charge_money, last_money = getRolling(id)
    if charge_money * 2 < last_money:
        return True, '롤링완료'
    else:
        return False, (charge_money * 2) - last_money

# 롤링 리셋
def resetRolling(id):
    execute_query("UPDATE user SET roll = ? WHERE id == ?;", ('0:0', id))
    execute_query("UPDATE user SET money = ? WHERE id == ?;", (0, id))
    return True

# 롤링 금액 조회
def getRolling(id):
    result = execute_query("SELECT roll FROM user WHERE id = ?;", (id,))
    if result:
        charge_money, last_money = map(int, result[0][0].split(':'))
        return charge_money, last_money
    return 0, 0


# 봇 상태 설정
intents = nextcord.Intents.default() 
intents.messages = True 
#------------------------------------------------------------
intents = nextcord.Intents.default() 
intents.messages = True  # 메시지 관련 이벤트 수신 허용
intents.message_content = True  # 메시지 내용 접근 허용

# 봇 객체 생성
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Game(config["bot_status"]), status=nextcord.Status.online)
    print("""
        ⢀⣤⣶⣶⣶⣦⣄⠀⠀⣶⣶⣆⠀⠀⢰⣶⡆⠀⣶⣶⡆⠀⠀⠀⣶⣶⠀⢰⣶⣶⣄⠀⠀⢰⣶⡆⠀⣶⣶⣶⣶⣶⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⠟⠉⠙⢿⣿⣆⠀⣿⣿⣿⣦⠀⢸⣿⡇⠀⣿⣿⡇⠀⠀⠀⣿⣿⠀⢸⣿⣿⣿⣦⠀⢸⣿⡇⠀⣿⣿⡏⠉⠉⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⠀⠀⢸⣿⣿⠀⣿⣿⠹⣿⣷⣸⣿⡇⠀⣿⣿⡇⠀⠀⠀⣿⣿⠀⢸⣿⣿⠻⣿⣧⣸⣿⡇⠀⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣆⣀⣠⣾⣿⠏⠀⣿⣿⠀⠘⢿⣿⣿⡇⠀⣿⣿⣇⣀⣀⠀⣿⣿⠀⢸⣿⣿⠀⠙⣿⣿⣿⡇⠀⣿⣿⣇⣀⣀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⠿⠿⠿⠿⠋⠀⠀⠿⠿⠀⠀⠈⠿⠿⠇⠀⠿⠿⠿⠿⠿⠇⠿⠿⠀⠸⠿⠿⠀⠀⠈⠿⠿⠇⠀⠿⠿⠿⠿⠿⠃⠀⠀⠀⠀⠀⠀""")

### Nextcord Admin Commands ###
from nextcord.ext import commands

@bot.command()
async def 수동충전(ctx, 금액: int, 유저: str):
    if ctx.author.id not in AdminList:
        return await ctx.send('허가되지 않은 접근입니다.')

    try:
        유저_id = int(유저.strip("<@!>"))
    except ValueError:
        return await ctx.send('잘못된 사용자 형식입니다. 유저 ID 또는 멘션을 사용하세요.')

    userResult = checkUser(유저_id)
    if not userResult:
        makeUserData(유저_id)

    adminAddUserMoney(유저_id, 금액)

    embed = nextcord.Embed(
        title='로나랜드 수동충전',
        description=f'**```css\n[ ✅ ] 성공적으로 유저에게 코인을 지급하였습니다.```**\n'
                    f'**```유저 ID : {유저_id}\n충전금 : {금액} 원\n유저 잔액 : {getUserMoney(유저_id)} 원```**'
    )
    await ctx.send(embed=embed)


@bot.command()
async def 회수(ctx, 금액: int, 유저: str):
    if ctx.author.id not in AdminList:
        return await ctx.send('**__허가되지 않은 접근입니다.__**')

    try:
        유저_id = int(유저.strip("<@!>"))
    except ValueError:
        return await ctx.send('잘못된 사용자 형식입니다. 유저 ID 또는 멘션을 사용하세요.')

    userResult = checkUser(유저_id)
    if not userResult:
        makeUserData(유저_id)

    if 금액 > int(getUserMoney(유저_id)):
        return await ctx.send(embed=makeEmbed('error', '잔액이 부족합니다...'))  # ✅ ephemeral 제거

    removeUserMoney(유저_id, 금액)

    embed = nextcord.Embed(
        title='로나랜드 코인회수',
        description=f'**```css\n[ ✅ ] 성공적으로 유저에게 코인을 회수하였습니다.```**\n'
                    f'**```유저 ID : {유저_id}\n회수금 : {금액} 원\n유저 잔액 : {getUserMoney(유저_id)} 원```**'
    )
    await ctx.send(embed=embed)

### Nextcord User Commands ###
@bot.command()
async def 충전(ctx, 금액: int):
    userResult = checkUser(ctx.author.id)
    if userResult == False:
        makeUserData(ctx.author.id)

    tossResult = makeTossRequest(금액)
    if tossResult == False:
        return await ctx.send(embed=makeEmbed('error', '충전 신청 중 오류가 발생하였습니다...'))

    class Confirm(nextcord.ui.View):
        def __init__(self):
            super().__init__()
            self.value = None

        @nextcord.ui.button(label='입금완료', style=nextcord.ButtonStyle.green)
        async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            self.value = True
            self.stop()

    view = Confirm()
    embed = nextcord.Embed(
        title='로나랜드 충전신청',
        description=f'**```css\n[ ✅ ] 성공적으로 충전신청을 진행했습니다.```**\n**```입금자명 : {tossResult[0]}\n입금계좌 : {tossResult[1]}```**\n**```❗❗❗ 꼭 입금을 완료하신 뒤 " 입금완료 " 버튼을 눌러주세요.```'
    )
    await ctx.send(embed=embed, view=view)
    await view.wait()

    if view.value:
        result = getTossConfirm(tossResult[0])
        if result[0] == True:
            try:
                con = sqlite3.connect('./database.db')
                cur = con.cursor()
                cur.execute(f'SELECT * FROM user WHERE id = {ctx.author.id}')
                result1 = cur.fetchone()
                last_m = result1[1]
                new_m = int(last_m) + int(금액)
                cur.execute("UPDATE user SET money = ? WHERE id == ?;", (new_m, ctx.author.id))
                con.commit()
                con.close()

                embed = nextcord.Embed(
                    title='로나랜드 충전성공',
                    description=f'**```css\n[ ✅ ] 성공적으로 충전을 진행했습니다.```**\n**```이전 잔액 : {last_m}\n신규 잔액 : {new_m}```**'
                )
                return await ctx.send(embed=embed)
            except Exception as e:
                print(e)
                return await ctx.send(embed=makeEmbed('error', '처리 도중 알 수 없는 오류가 발생하였습니다...'))
        elif result[0] == False:
            return await ctx.send(embed=makeEmbed('error', f'{result[1]}'))
        else:
            return await ctx.send(embed=makeEmbed('error', '처리 도중 알 수 없는 오류가 발생하였습니다...'))

@bot.command()
async def 잔액(ctx):
    userResult = checkUser(ctx.author.id) 
    if userResult == False: 
        makeUserData(ctx.author.id) 
    
    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    cur.execute(f'SELECT * FROM user WHERE id = {ctx.author.id}')
    result = cur.fetchone()
    
    embed = nextcord.Embed(
        title='로나랜드 잔액확인',
        description=f'**```css\n[ ✅ ] 성공적으로 잔액을 확인했습니다.```**\n**```잔액 : {result[1]} 원```**'
    )
    await ctx.send(embed=embed)


@bot.command()
async def 롤링(ctx):
    result = checkRolling(ctx.author.id)
    if result[1] == False:
        embed = nextcord.Embed(
            title='로나랜드 롤링확인',
            description=f'**```css\n[ ⛔ ] 롤링을 완료하지 못했습니다.\n남은 롤링액은 : {result[1]} 원 입니다.```**'
        )
        await ctx.send(embed=embed)
    elif result:
        embed = nextcord.Embed(
            title='로나랜드 롤링확인',
            description=f'**```css\n[ ✅ ] 성공적으로 롤링을 완료했습니다.```**'
        )
        await ctx.send(embed=embed)

@bot.command()
async def 롤링초기화(ctx):
    result = resetRolling(ctx.author.id)
    if result:
        embed = nextcord.Embed(
            title='로나랜드 롤링 초기화',
            description=f'**```css\n[ ✅ ] 성공적으로 롤링/잔여금 을 초기화했습니다.```**'
        )
        await ctx.send(embed=embed)


@bot.command()
async def 다이스(ctx, 배팅액: int, 언옵: str = None):
    
    if 언옵 is None or 언옵.upper() not in ["OVER", "UNDER"]:
        embed = nextcord.Embed(
            title="로나랜드 오리지널 다이스",
            description="**```css\n[ ❌ ] 잘못된 배팅입니다! 'UNDER' 또는 'OVER'로 입력해주세요!```**"
        )

        await ctx.send(embed=embed)
        return
        
    num = random.randint(1, 6)
    userResult = checkUser(ctx.author.id) 
    if userResult == False: 
        makeUserData(ctx.author.id) 
    
    if 배팅액 > int(getUserMoney(ctx.author.id)):
        return await ctx.send(embed=makeEmbed('error', '잔액이 부족합니다...'))
    
    addRolling(ctx.author.id, 배팅액)
    if removeUserMoney(ctx.author.id, 배팅액):
        if num >= 4:
            if 언옵 == 'OVER':  # 승리
                addUserMoney(ctx.author.id, round(배팅액 * 1.8))
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 다이스',
                    description=f'**```css\n[ ✅ ] 다이스 진행 결과.. 승리```**\n**```주사위 : {num}ㅣ결과 : 오버ㅣ배팅 : 오버ㅣ승리금 : {round(배팅액 * 1.8)} 원```**'
                )
                await ctx.send(embed=embed)
            elif 언옵 == 'UNDER':  # 패배
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 다이스',
                    description=f'**```css\n[ ✅ ] 다이스 진행 결과.. 패배```**\n**```주사위 : {num}ㅣ결과 : 오버ㅣ배팅 : 언더ㅣ패배금 : {배팅액} 원```**'
                )
                await ctx.send(embed=embed)
        if num <= 3:
            if 언옵 == 'UNDER':  # 승리
                addUserMoney(ctx.author.id, round(배팅액 * 1.8))
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 다이스',
                    description=f'**```css\n[ ✅ ] 다이스 진행 결과.. 승리```**\n**```주사위 : {num}ㅣ결과 : 언더ㅣ배팅 : 언더ㅣ승리금 : {round(배팅액 * 1.8)} 원```**'
                )
                await ctx.send(embed=embed)
            else:  # 패배
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 다이스',
                    description=f'**```css\n[ ✅ ] 다이스 진행 결과.. 패배```**\n**```주사위 : {num}ㅣ결과 : 언더ㅣ배팅 : 오버ㅣ패배금 : {배팅액} 원```**'
                )
                await ctx.send(embed=embed)
                
@bot.command()
async def 온오프(ctx, 배팅액: int, 온오프: str):
    if 온오프.upper() not in ["OFF", "ON"]:
           embed = nextcord.Embed(
                    title='로나랜드 오리지널 온오프',
                    description=f'**```css\n[ ❌ ] 잘못된 배팅입니다!  On,off로 입력해주세요!```**')
    num = random.randint(0, 1)
    userResult = checkUser(ctx.author.id)
    if userResult == False:
        makeUserData(ctx.author.id)

    if 배팅액 > int(getUserMoney(ctx.author.id)):
        return await ctx.send(embed=makeEmbed('error', '잔액이 부족합니다...'))

    addRolling(ctx.author.id, 배팅액)

    if removeUserMoney(ctx.author.id, 배팅액):
        if num == 0:
            if 온오프 == 'ON':  # 승리
                addUserMoney(ctx.author.id, round(배팅액 * 1.5))
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 온오프',
                    description=f'**```css\n[ ✅ ] 온오프 진행 결과.. 승리```**\n**```결과 : 온라인ㅣ배팅 : 온라인ㅣ승리금 : {round(배팅액 * 1.5)} 원```'
                )
                await ctx.send(embed=embed)
            else:  # 패배
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 온오프',
                    description=f'**```css\n[ ✅ ] 온오프 진행 결과.. 패배```**\n**```결과 : 온라인ㅣ배팅 : 오프라인ㅣ패배금 : {배팅액} 원```'
                )
                await ctx.send(embed=embed)

        if num == 1:
            if 온오프 == 'OFF':  # 승리
                addUserMoney(ctx.author.id, round(배팅액 * 1.5))
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 온오프',
                    description=f'**```css\n[ ✅ ] 온오프 진행 결과.. 승리```**\n**```결과 : 오프라인ㅣ배팅 : 오프라인ㅣ승리금 : {round(배팅액 * 1.5)} 원```'
                )
                await ctx.send(embed=embed)
            else:  # 패배
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 온오프',
                    description=f'**```css\n[ ✅ ] 온오프 진행 결과.. 패배```**\n**```결과 : 오프라인ㅣ배팅 : 온라인ㅣ패배금 : {배팅액} 원```'
                )
                await ctx.send(embed=embed)

@bot.command()
async def 경마(ctx, 배팅액: int, 말: int):

    if 말 < 1 or 말 > 5:
       embed = nextcord.Embed(
                title='로나랜드 오리지널 경마',
                description=f'**```css\n[ ❌ ] 잘못된 배팅입니다! 말의 번호는 1에서 5번까지있습니다! 다시시도해주세요!```**'
            )
    
    arr = [1, 2, 3, 4, 5]
    random.shuffle(arr)  # 왼쪽에서부터 1등

    userResult = checkUser(ctx.author.id)
    if userResult == False:
        makeUserData(ctx.author.id)

    if 배팅액 > int(getUserMoney(ctx.author.id)):
        return await ctx.send(embed=makeEmbed('error', '잔액이 부족합니다...'))



    addRolling(ctx.author.id, 배팅액)

    if removeUserMoney(ctx.author.id, 배팅액):
        if arr[0] == 말:  # 1등
            addUserMoney(ctx.author.id, round(배팅액 * 2))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 경마',
                description=f'**```css\n[ ✅ ] 경마 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ배팅 : {말}번말ㅣ승리금 : {round(배팅액 * 2)} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)
        elif arr[1] == 말:  # 2등
            addUserMoney(ctx.author.id, round(배팅액 * 1.7))
            embed = nextcord.Embed(
                title='로나랜드 오리지널경마',
                description=f'**```css\n[ ✅ ] 경마 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ배팅 : {말}번말ㅣ승리금 : {round(배팅액 * 1.7)} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)
        else:
            embed = nextcord.Embed(
                title='로나랜드 오리지널 경마',
                description=f'**```css\n[ ✅ ] 말달리기 진행 결과.. 패배```**\n**```경기결과 : [하단참조]ㅣ배팅 : {말}번말ㅣ패배금 : {배팅액} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)

@bot.command()
async def 마리오(ctx, 배팅액: int):
    arr = ['A', 'J', 'M', 'T', 'F', 'F', 'F', 'F', 'F']
    random.shuffle(arr)  # A , J 조커 , M 마리오 , T 터틀 , F 탈락

    userResult = checkUser(ctx.author.id)
    if userResult == False:
        makeUserData(ctx.author.id)

    if 배팅액 > int(getUserMoney(ctx.author.id)):
        return await ctx.send(embed=makeEmbed('error', '잔액이 부족합니다...'))

    addRolling(ctx.author.id, 배팅액)

    if removeUserMoney(ctx.author.id, 배팅액):
        if arr[0] == 'A':
            addUserMoney(ctx.author.id, round(배팅액 * 2))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 마리오',
                description=f'**```css\n[ ✅ ] 마리오 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 2)} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)
        elif arr[0] == 'J':
            addUserMoney(ctx.author.id, round(배팅액 * 2.5))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 마리오',
                description=f'**```css\n[ ✅ ] 마리오 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 2.5)} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)
        elif arr[0] == 'M':
            addUserMoney(ctx.author.id, round(배팅액 * 3))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 마리오',
                description=f'**```css\n[ ✅ ] 마리오 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 3)} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)
        elif arr[0] == 'T':
            addUserMoney(ctx.author.id, round(배팅액 * 0.5))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 마리오',
                description=f'**```css\n[ ✅ ] 마리오 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 0.5)} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)
        elif arr[0] == 'F':
            embed = nextcord.Embed(
                title='로나랜드 오리지널 마리오',
                description=f'**```css\n[ ✅ ] 마리오 진행 결과.. 패배```**\n**```경기결과 : [하단참조]ㅣ패배금 : {배팅액} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)
        
@bot.command()
async def 로또(ctx, 배팅액: int, 일번볼: int, 이번볼: int, 삼번볼: int, 사번볼: int, 오번볼: int, 육번볼: int, 칠번볼: int):
    userResult = checkUser(ctx.author.id)
    if userResult == False:
        makeUserData(ctx.author.id)

    if 배팅액 > int(getUserMoney(ctx.author.id)):
        return await ctx.send(embed=makeEmbed('error', '잔액이 부족합니다...'))

    addRolling(ctx.author.id, 배팅액)

    user_data = {
        "1": 일번볼,
        "2": 이번볼,
        "3": 삼번볼,
        "4": 사번볼,
        "5": 오번볼,
        "6": 육번볼,
        "7": 칠번볼,
    }
    server_data = {
        "1": random.randint(1, 10),
        "2": random.randint(1, 10),
        "3": random.randint(1, 10),
        "4": random.randint(1, 10),
        "5": random.randint(1, 10),
        "6": random.randint(1, 10),
        "7": random.randint(1, 10),
    }

    true_data = 0
    for i in range(7):
        if user_data[f"{i + 1}"] == server_data[f"{i + 1}"]:
            true_data = true_data + 1

    if removeUserMoney(ctx.author.id, 배팅액):
        if true_data == 6:
            addUserMoney(ctx.author.id, round(배팅액 * 8))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 로또',
                description=f'**```css\n[ ✅ ] 로또 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 8)} 원```**\n**```서버 결과\nㄴ {server_data}\n유저 결과\nㄴ {user_data}\n당첨볼 : {true_data} 개```'
            )
            return await ctx.send(embed=embed)
        elif true_data >= 4:
            addUserMoney(ctx.author.id, round(배팅액 * 4))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 로또',
                description=f'**```css\n[ ✅ ] 로또 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 4)} 원```**\n**```서버 결과\nㄴ {server_data}\n유저 결과\nㄴ {user_data}\n당첨볼 : {true_data} 개```'
            )
            return await ctx.send(embed=embed)
        elif true_data >= 3:
            addUserMoney(ctx.author.id, round(배팅액 * 2))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 로또',
                description=f'**```css\n[ ✅ ] 로또 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 2)} 원```**\n**```서버 결과\nㄴ {server_data}\n유저 결과\nㄴ {user_data}\n당첨볼 : {true_data} 개```'
            )
            return await ctx.send(embed=embed)
        elif true_data >= 2:
            addUserMoney(ctx.author.id, round(배팅액 * 0.5))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 로또',
                description=f'**```css\n[ ✅ ] 로또 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 0.5)} 원```**\n**```서버 결과\nㄴ {server_data}\n유저 결과\nㄴ {user_data}\n당첨볼 : {true_data} 개```'
            )
            return await ctx.send(embed=embed)
        elif true_data <= 1:
            embed = nextcord.Embed(
                title='로나랜드 오리지널 로또',
                description=f'**```css\n[ ✅ ] 로또 진행 결과.. 패배```**\n**```경기결과 : [하단참조]ㅣ패배금 : {배팅액} 원```**\n**```서버 결과\nㄴ {server_data}\n유저 결과\nㄴ {user_data}\n당첨볼 : {true_data} 개```'
            )
            await ctx.send(embed=embed)
# 도움말 명령어
@bot.command()
async def 도움말(ctx):
    embed = nextcord.Embed(
        title="📜 도움말 명령어 목록",
        description="사용 가능한 명령어들입니다!",
        color=0x00FF00  # 초록색
    )

    embed.add_field(name="🎰 !로또 [1번호] [2번호] [3번호] [4번호] [5번호] [6번호] [7번호]", value="랜덤 로또 번호를 구매합니다. (8배,1~10까지의번호)", inline=False)
    embed.add_field(name="💰 !잔액", value="현재 보유한 잔액을 확인합니다!", inline=False)
    embed.add_field(name="🎁 !마리오 [A,J,M,T] [금액]", value="포인트 충전을 요청합니다.(최대 3베)", inline=False)
    embed.add_field(name="🎲 !다이스[금액] [OVER,UNDER]", value="구매한 로또 번호를 확인합니다.(1.8배)", inline=False)
    embed.add_field(name="🏇 !경마 [말] [배팅액]", value="경마에 배팅합니다.(최대2배)", inline=False)
    embed.add_field(name="🔲 !온오프 [배팅액] [ON,OFF]", value="이 도움말을 표시합니다.(1.5배)", inline=False)

    embed.set_footer(text="로나랜드 2세 | 문의: 문의채널")
    
    await ctx.send(embed=embed)

# 봇 실행
bot.run(config["token"])
### Config ###
import nextcord
from nextcord.ext import commands
import random
import sqlite3

import toss


config = {
    ### Discord Config ###
    "token": "MTM0MzE4MTY0NzM3MzQwMjE1NA.GcAIKR.u0WPIlZtlNVhr-gSBSnx08FLURRj4NahKHW_ro",
    "guild_id": 1343156808230899725,
    "bot_status": "로나랜드 오리지널",
    ### Toss Config ###
    "toss_token": "",
    "toss_id": ""
}

AdminList = [1251376918335455259,1339650919553437729]

def execute_query(query, params=()):
    try:
        con = sqlite3.connect('./database.db')
        cur = con.cursor()
        cur.execute(query, params)
        result = cur.fetchall()
        con.commit()
        con.close()
        return result
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None

# Toss 요청 함수
def makeTossRequest(amount):
    result = toss.request(token=config['toss_token'], toss_id=config["toss_id"], amount=amount)
    if result == 'FAIL':
        return False
    else:
        return result

# Toss 확인 함수
def getTossConfirm(code):
    result = toss.confirm(token=config["toss_token"], code=code)
    if result['result'] == 'FAIL':
        return False, result['message']
    else:
        return True, result['message']

# 사용자 존재 여부 확인
def checkUser(id):
    result = execute_query("SELECT * FROM user WHERE id == ?;", (id,))
    return bool(result)

# 사용자 데이터 생성
def makeUserData(id):
    execute_query("INSERT INTO user VALUES(?, ?, ?)", (id, 0, '0:0'))
    return True

# 임베드 메시지 생성
def makeEmbed(code, des):
    if code == 'error':
        embed = nextcord.Embed(
            title='로나랜드 오류알림',
            description=f'**```css\n[ ⛔ ] {des}```**'
        )
    else:
        embed = nextcord.Embed(
            title='로나랜드 알림',
            description=f'**```css\n[ ℹ️ ] {des}```**'
        )
    return embed

# 사용자 금액 조회
def getUserMoney(id):
    result = execute_query("SELECT * FROM user WHERE id = ?;", (id,))
    return result[0][1] if result else 0

# 사용자 금액 차감
def removeUserMoney(id, money):
    last_money = getUserMoney(id)
    new_money = last_money - int(money)
    execute_query("UPDATE user SET money = ? WHERE id == ?;", (new_money, id))
    return True

# 관리자 금액 수정
def adminAddUserMoney(id, money):
    execute_query("UPDATE user SET money = ? WHERE id == ?;", (money, id))
    execute_query("UPDATE user SET roll = ? WHERE id == ?;", (f'{money}:0', id))
    return True

# 사용자 금액 추가
def addUserMoney(id, money):
    last_money = getUserMoney(id)
    new_money = last_money + int(money)
    execute_query("UPDATE user SET money = ? WHERE id == ?;", (new_money, id))
    return True

# 롤링 금액 추가
def addRolling(id, money):
    charge_money, last_money = getRolling(id)
    new_money = last_money + int(money)
    execute_query("UPDATE user SET roll = ? WHERE id == ?;", (f'{charge_money}:{new_money}', id))
    return True

# 롤링 확인
def checkRolling(id):
    charge_money, last_money = getRolling(id)
    if charge_money * 2 < last_money:
        return True, '롤링완료'
    else:
        return False, (charge_money * 2) - last_money

# 롤링 리셋
def resetRolling(id):
    execute_query("UPDATE user SET roll = ? WHERE id == ?;", ('0:0', id))
    execute_query("UPDATE user SET money = ? WHERE id == ?;", (0, id))
    return True

# 롤링 금액 조회
def getRolling(id):
    result = execute_query("SELECT roll FROM user WHERE id = ?;", (id,))
    if result:
        charge_money, last_money = map(int, result[0][0].split(':'))
        return charge_money, last_money
    return 0, 0


# 봇 상태 설정
intents = nextcord.Intents.default() 
intents.messages = True 
#------------------------------------------------------------
intents = nextcord.Intents.default() 
intents.messages = True  # 메시지 관련 이벤트 수신 허용
intents.message_content = True  # 메시지 내용 접근 허용

# 봇 객체 생성
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Game(config["bot_status"]), status=nextcord.Status.online)
    print("""
        ⢀⣤⣶⣶⣶⣦⣄⠀⠀⣶⣶⣆⠀⠀⢰⣶⡆⠀⣶⣶⡆⠀⠀⠀⣶⣶⠀⢰⣶⣶⣄⠀⠀⢰⣶⡆⠀⣶⣶⣶⣶⣶⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⠟⠉⠙⢿⣿⣆⠀⣿⣿⣿⣦⠀⢸⣿⡇⠀⣿⣿⡇⠀⠀⠀⣿⣿⠀⢸⣿⣿⣿⣦⠀⢸⣿⡇⠀⣿⣿⡏⠉⠉⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⠀⠀⢸⣿⣿⠀⣿⣿⠹⣿⣷⣸⣿⡇⠀⣿⣿⡇⠀⠀⠀⣿⣿⠀⢸⣿⣿⠻⣿⣧⣸⣿⡇⠀⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣆⣀⣠⣾⣿⠏⠀⣿⣿⠀⠘⢿⣿⣿⡇⠀⣿⣿⣇⣀⣀⠀⣿⣿⠀⢸⣿⣿⠀⠙⣿⣿⣿⡇⠀⣿⣿⣇⣀⣀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⠿⠿⠿⠿⠋⠀⠀⠿⠿⠀⠀⠈⠿⠿⠇⠀⠿⠿⠿⠿⠿⠇⠿⠿⠀⠸⠿⠿⠀⠀⠈⠿⠿⠇⠀⠿⠿⠿⠿⠿⠃⠀⠀⠀⠀⠀⠀""")

### Nextcord Admin Commands ###
from nextcord.ext import commands

@bot.command()
async def 수동충전(ctx, 금액: int, 유저: str):
    if ctx.author.id not in AdminList:
        return await ctx.send('허가되지 않은 접근입니다.')

    try:
        유저_id = int(유저.strip("<@!>"))
    except ValueError:
        return await ctx.send('잘못된 사용자 형식입니다. 유저 ID 또는 멘션을 사용하세요.')

    userResult = checkUser(유저_id)
    if not userResult:
        makeUserData(유저_id)

    adminAddUserMoney(유저_id, 금액)

    embed = nextcord.Embed(
        title='로나랜드 수동충전',
        description=f'**```css\n[ ✅ ] 성공적으로 유저에게 코인을 지급하였습니다.```**\n'
                    f'**```유저 ID : {유저_id}\n충전금 : {금액} 원\n유저 잔액 : {getUserMoney(유저_id)} 원```**'
    )
    await ctx.send(embed=embed)


@bot.command()
async def 회수(ctx, 금액: int, 유저: str):
    if ctx.author.id not in AdminList:
        return await ctx.send('**__허가되지 않은 접근입니다.__**')

    try:
        유저_id = int(유저.strip("<@!>"))
    except ValueError:
        return await ctx.send('잘못된 사용자 형식입니다. 유저 ID 또는 멘션을 사용하세요.')

    userResult = checkUser(유저_id)
    if not userResult:
        makeUserData(유저_id)

    if 금액 > int(getUserMoney(유저_id)):
        return await ctx.send(embed=makeEmbed('error', '잔액이 부족합니다...'))  # ✅ ephemeral 제거

    removeUserMoney(유저_id, 금액)

    embed = nextcord.Embed(
        title='로나랜드 코인회수',
        description=f'**```css\n[ ✅ ] 성공적으로 유저에게 코인을 회수하였습니다.```**\n'
                    f'**```유저 ID : {유저_id}\n회수금 : {금액} 원\n유저 잔액 : {getUserMoney(유저_id)} 원```**'
    )
    await ctx.send(embed=embed)

### Nextcord User Commands ###
@bot.command()
async def 충전(ctx, 금액: int):
    userResult = checkUser(ctx.author.id)
    if userResult == False:
        makeUserData(ctx.author.id)

    tossResult = makeTossRequest(금액)
    if tossResult == False:
        return await ctx.send(embed=makeEmbed('error', '충전 신청 중 오류가 발생하였습니다...'))

    class Confirm(nextcord.ui.View):
        def __init__(self):
            super().__init__()
            self.value = None

        @nextcord.ui.button(label='입금완료', style=nextcord.ButtonStyle.green)
        async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            self.value = True
            self.stop()

    view = Confirm()
    embed = nextcord.Embed(
        title='로나랜드 충전신청',
        description=f'**```css\n[ ✅ ] 성공적으로 충전신청을 진행했습니다.```**\n**```입금자명 : {tossResult[0]}\n입금계좌 : {tossResult[1]}```**\n**```❗❗❗ 꼭 입금을 완료하신 뒤 " 입금완료 " 버튼을 눌러주세요.```'
    )
    await ctx.send(embed=embed, view=view)
    await view.wait()

    if view.value:
        result = getTossConfirm(tossResult[0])
        if result[0] == True:
            try:
                con = sqlite3.connect('./database.db')
                cur = con.cursor()
                cur.execute(f'SELECT * FROM user WHERE id = {ctx.author.id}')
                result1 = cur.fetchone()
                last_m = result1[1]
                new_m = int(last_m) + int(금액)
                cur.execute("UPDATE user SET money = ? WHERE id == ?;", (new_m, ctx.author.id))
                con.commit()
                con.close()

                embed = nextcord.Embed(
                    title='로나랜드 충전성공',
                    description=f'**```css\n[ ✅ ] 성공적으로 충전을 진행했습니다.```**\n**```이전 잔액 : {last_m}\n신규 잔액 : {new_m}```**'
                )
                return await ctx.send(embed=embed)
            except Exception as e:
                print(e)
                return await ctx.send(embed=makeEmbed('error', '처리 도중 알 수 없는 오류가 발생하였습니다...'))
        elif result[0] == False:
            return await ctx.send(embed=makeEmbed('error', f'{result[1]}'))
        else:
            return await ctx.send(embed=makeEmbed('error', '처리 도중 알 수 없는 오류가 발생하였습니다...'))

@bot.command()
async def 잔액(ctx):
    userResult = checkUser(ctx.author.id) 
    if userResult == False: 
        makeUserData(ctx.author.id) 

    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    cur.execute(f'SELECT * FROM user WHERE id = {ctx.author.id}')
    result = cur.fetchone()

    embed = nextcord.Embed(
        title='로나랜드 잔액확인',
        description=f'**```css\n[ ✅ ] 성공적으로 잔액을 확인했습니다.```**\n**```잔액 : {result[1]} 원```**'
    )
    await ctx.send(embed=embed)


@bot.command()
async def 롤링(ctx):
    result = checkRolling(ctx.author.id)
    if result[0] == False:
        embed = nextcord.Embed(
            title='로나랜드 롤링확인',
            description=f'**```css\n[ ⛔ ] 롤링을 완료하지 못했습니다.\n남은 롤링액은 : {result[1]} 원 입니다.```**'
        )
        await ctx.send(embed=embed)
    elif result:
        embed = nextcord.Embed(
            title='로나랜드 롤링확인',
            description=f'**```css\n[ ✅ ] 성공적으로 롤링을 완료했습니다.```**'
        )
        await ctx.send(embed=embed)

@bot.command()
async def 롤링초기화(ctx):
    result = resetRolling(ctx.author.id)
    if result:
        embed = nextcord.Embed(
            title='로나랜드 롤링 초기화',
            description=f'**```css\n[ ✅ ] 성공적으로 롤링/잔여금 을 초기화했습니다.```**'
        )
        await ctx.send(embed=embed)


@bot.command()
async def 다이스(ctx, 배팅액: int, 언옵: str = None):
    num = random.randint(1, 6)
    userResult = checkUser(ctx.author.id) 
    if userResult == False: 
        makeUserData(ctx.author.id) 

    if 배팅액 > int(getUserMoney(ctx.author.id)):
        return await ctx.send(embed=makeEmbed('error', '잔액이 부족합니다...'))

    addRolling(ctx.author.id, 배팅액)
    if removeUserMoney(ctx.author.id, 배팅액):
        if num >= 4:
            if 언옵 == 'OVER':  # 승리
                addUserMoney(ctx.author.id, round(배팅액 * 1.8))
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 다이스',
                    description=f'**```css\n[ ✅ ] 다이스 진행 결과.. 승리```**\n**```주사위 : {num}ㅣ결과 : 오버ㅣ배팅 : 오버ㅣ승리금 : {round(배팅액 * 1.8)} 원```**'
                )
                await ctx.send(embed=embed)
            elif 언옵 == 'UNDER':  # 패배
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 다이스',
                    description=f'**```css\n[ ✅ ] 다이스 진행 결과.. 패배```**\n**```주사위 : {num}ㅣ결과 : 오버ㅣ배팅 : 언더ㅣ패배금 : {배팅액} 원```**'
                )
                await ctx.send(embed=embed)
        if num <= 3:
            if 언옵 == 'UNDER':  # 승리
                addUserMoney(ctx.author.id, round(배팅액 * 1.8))
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 다이스',
                    description=f'**```css\n[ ✅ ] 다이스 진행 결과.. 승리```**\n**```주사위 : {num}ㅣ결과 : 언더ㅣ배팅 : 언더ㅣ승리금 : {round(배팅액 * 1.8)} 원```**'
                )
                await ctx.send(embed=embed)
            else:  # 패배
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 다이스',
                    description=f'**```css\n[ ✅ ] 다이스 진행 결과.. 패배```**\n**```주사위 : {num}ㅣ결과 : 언더ㅣ배팅 : 오버ㅣ패배금 : {배팅액} 원```**'
                )
                await ctx.send(embed=embed)

@bot.command()
async def 온오프(ctx, 배팅액: int, 온오프: str):
    num = random.randint(0, 1)
    userResult = checkUser(ctx.author.id)
    if userResult == False:
        makeUserData(ctx.author.id)

    if 배팅액 > int(getUserMoney(ctx.author.id)):
        return await ctx.send(embed=makeEmbed('error', '잔액이 부족합니다...'))

    addRolling(ctx.author.id, 배팅액)

    if removeUserMoney(ctx.author.id, 배팅액):
        if num == 0:
            if 온오프 == 'ON':  # 승리
                addUserMoney(ctx.author.id, round(배팅액 * 1.5))
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 온오프',
                    description=f'**```css\n[ ✅ ] 온오프 진행 결과.. 승리```**\n**```결과 : 온라인ㅣ배팅 : 온라인ㅣ승리금 : {round(배팅액 * 1.5)} 원```'
                )
                await ctx.send(embed=embed)
            else:  # 패배
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 온오프',
                    description=f'**```css\n[ ✅ ] 온오프 진행 결과.. 패배```**\n**```결과 : 온라인ㅣ배팅 : 오프라인ㅣ패배금 : {배팅액} 원```'
                )
                await ctx.send(embed=embed)

        if num == 1:
            if 온오프 == 'OFF':  # 승리
                addUserMoney(ctx.author.id, round(배팅액 * 1.5))
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 온오프',
                    description=f'**```css\n[ ✅ ] 온오프 진행 결과.. 승리```**\n**```결과 : 오프라인ㅣ배팅 : 오프라인ㅣ승리금 : {round(배팅액 * 1.5)} 원```'
                )
                await ctx.send(embed=embed)
            else:  # 패배
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 온오프',
                    description=f'**```css\n[ ✅ ] 온오프 진행 결과.. 패배```**\n**```결과 : 오프라인ㅣ배팅 : 온라인ㅣ패배금 : {배팅액} 원```'
                )
                await ctx.send(embed=embed)

@bot.command()
async def 경마(ctx, 배팅액: int, 말: int):

    if 말 < 1 or 말 > 5:
       embed = nextcord.Embed(
                title='로나랜드 오리지널 경마',
                description=f'**```css\n[ ❌ ] 잘못된 배팅입니다! 말의 번호는 1에서 5번까지있습니다! 다시시도해주세요!```**'
            )

    arr = [1, 2, 3, 4, 5]
    random.shuffle(arr)  # 왼쪽에서부터 1등

    userResult = checkUser(ctx.author.id)
    if userResult == False:
        makeUserData(ctx.author.id)

    if 배팅액 > int(getUserMoney(ctx.author.id)):
        return await ctx.send(embed=makeEmbed('error', '잔액이 부족합니다...'))



    addRolling(ctx.author.id, 배팅액)

    if removeUserMoney(ctx.author.id, 배팅액):
        if arr[0] == 말:  # 1등
            addUserMoney(ctx.author.id, round(배팅액 * 2))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 경마',
                description=f'**```css\n[ ✅ ] 경마 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ배팅 : {말}번말ㅣ승리금 : {round(배팅액 * 2)} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)
        elif arr[1] == 말:  # 2등
            addUserMoney(ctx.author.id, round(배팅액 * 1.7))
            embed = nextcord.Embed(
                title='로나랜드 오리지널경마',
                description=f'**```css\n[ ✅ ] 경마 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ배팅 : {말}번말ㅣ승리금 : {round(배팅액 * 1.7)} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)
        else:
            embed = nextcord.Embed(
                title='로나랜드 오리지널 경마',
                description=f'**```css\n[ ✅ ] 말달리기 진행 결과.. 패배```**\n**```경기결과 : [하단참조]ㅣ배팅 : {말}번말ㅣ패배금 : {배팅액} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)

@bot.command()
async def 마리오(ctx, 배팅액: int):
    arr = ['A', 'J', 'M', 'T', 'F', 'F', 'F', 'F', 'F']
    random.shuffle(arr)  # A , J 조커 , M 마리오 , T 터틀 , F 탈락

    userResult = checkUser(ctx.author.id)
    if userResult == False:
        makeUserData(ctx.author.id)

    if 배팅액 > int(getUserMoney(ctx.author.id)):
        return await ctx.send(embed=makeEmbed('error', '잔액이 부족합니다...'))

    addRolling(ctx.author.id, 배팅액)

    if removeUserMoney(ctx.author.id, 배팅액):
        if arr[0] == 'A':
            addUserMoney(ctx.author.id, round(배팅액 * 2))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 마리오',
                description=f'**```css\n[ ✅ ] 마리오 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 2)} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)
        elif arr[0] == 'J':
            addUserMoney(ctx.author.id, round(배팅액 * 2.5))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 마리오',
                description=f'**```css\n[ ✅ ] 마리오 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 2.5)} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)
        elif arr[0] == 'M':
            addUserMoney(ctx.author.id, round(배팅액 * 3))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 마리오',
                description=f'**```css\n[ ✅ ] 마리오 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 3)} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)
        elif arr[0] == 'T':
            addUserMoney(ctx.author.id, round(배팅액 * 0.5))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 마리오',
                description=f'**```css\n[ ✅ ] 마리오 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 0.5)} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)
        elif arr[0] == 'F':
            embed = nextcord.Embed(
                title='로나랜드 오리지널 마리오',
                description=f'**```css\n[ ✅ ] 마리오 진행 결과.. 패배```**\n**```경기결과 : [하단참조]ㅣ패배금 : {배팅액} 원```**\n**```{arr}```**'
            )
            await ctx.send(embed=embed)

@bot.command()
async def 로또(ctx, 배팅액: int, 일번볼: int, 이번볼: int, 삼번볼: int, 사번볼: int, 오번볼: int, 육번볼: int, 칠번볼: int):
    userResult = checkUser(ctx.author.id)
    if userResult == False:
        makeUserData(ctx.author.id)

    if 배팅액 > int(getUserMoney(ctx.author.id)):
        return await ctx.send(embed=makeEmbed('error', '잔액이 부족합니다...'))

    addRolling(ctx.author.id, 배팅액)

    user_data = {
        "1": 일번볼,
        "2": 이번볼,
        "3": 삼번볼,
        "4": 사번볼,
        "5": 오번볼,
        "6": 육번볼,
        "7": 칠번볼,
    }
    server_data = {
        "1": random.randint(1, 10),
        "2": random.randint(1, 10),
        "3": random.randint(1, 10),
        "4": random.randint(1, 10),
        "5": random.randint(1, 10),
        "6": random.randint(1, 10),
        "7": random.randint(1, 10),
    }

    true_data = 0
    for i in range(7):
        if user_data[f"{i + 1}"] == server_data[f"{i + 1}"]:
            true_data = true_data + 1

    if removeUserMoney(ctx.author.id, 배팅액):
        if true_data == 6:
            addUserMoney(ctx.author.id, round(배팅액 * 8))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 로또',
                description=f'**```css\n[ ✅ ] 로또 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 8)} 원```**\n**```서버 결과\nㄴ {server_data}\n유저 결과\nㄴ {user_data}\n당첨볼 : {true_data} 개```'
            )
            return await ctx.send(embed=embed)
        elif true_data >= 4:
            addUserMoney(ctx.author.id, round(배팅액 * 4))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 로또',
                description=f'**```css\n[ ✅ ] 로또 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 4)} 원```**\n**```서버 결과\nㄴ {server_data}\n유저 결과\nㄴ {user_data}\n당첨볼 : {true_data} 개```'
            )
            return await ctx.send(embed=embed)
        elif true_data >= 3:
            addUserMoney(ctx.author.id, round(배팅액 * 2))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 로또',
                description=f'**```css\n[ ✅ ] 로또 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 2)} 원```**\n**```서버 결과\nㄴ {server_data}\n유저 결과\nㄴ {user_data}\n당첨볼 : {true_data} 개```'
            )
            return await ctx.send(embed=embed)
        elif true_data >= 2:
            addUserMoney(ctx.author.id, round(배팅액 * 0.5))
            embed = nextcord.Embed(
                title='로나랜드 오리지널 로또',
                description=f'**```css\n[ ✅ ] 로또 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 0.5)} 원```**\n**```서버 결과\nㄴ {server_data}\n유저 결과\nㄴ {user_data}\n당첨볼 : {true_data} 개```'
            )
            return await ctx.send(embed=embed)
        elif true_data <= 1:
            embed = nextcord.Embed(
                title='로나랜드 오리지널 로또',
                description=f'**```css\n[ ✅ ] 로또 진행 결과.. 패배```**\n**```경기결과 : [하단참조]ㅣ패배금 : {배팅액} 원```**\n**```서버 결과\nㄴ {server_data}\n유저 결과\nㄴ {user_data}\n당첨볼 : {true_data} 개```'
            )
            await ctx.send(embed=embed)
# 도움말 명령어
@bot.command()
async def 도움말(ctx):
    embed = nextcord.Embed(
        title="📜 도움말 명령어 목록",
        description="사용 가능한 명령어들입니다!",
        color=0x00FF00  # 초록색
    )

    embed.add_field(name="🎰 !로또 [1번호] [2번호] [3번호] [4번호] [5번호] [6번호] [7번호]", value="랜덤 로또 번호를 구매합니다. (8배,1~10까지의번호)", inline=False)
    embed.add_field(name="💰 !잔액", value="현재 보유한 잔액을 확인합니다!", inline=False)
    embed.add_field(name="🎁 !마리오 [A,J,M,T] [금액]", value="포인트 충전을 요청합니다.(최대 3베)", inline=False)
    embed.add_field(name="🎲 !다이스[금액] [OVER,UNDER]", value="구매한 로또 번호를 확인합니다.(1.8배)", inline=False)
    embed.add_field(name="🏇 !경마 [말] [배팅액]", value="경마에 배팅합니다.(최대2배)", inline=False)
    embed.add_field(name="🔲 !온오프 [배팅액] [ON,OFF]", value="이 도움말을 표시합니다.(1.5배)", inline=False)

    embed.set_footer(text="로나랜드 2세 | 문의: 문의채널")

    await ctx.send(embed=embed)

# 봇 실행
bot.run(config["token"])
