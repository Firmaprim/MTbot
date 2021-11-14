from discord import *
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
import datetime

MT_LEVELS = {
    0:    "#888888",
    70:   "#08D508",
    200:  "#008800",
    400:  "#00BBEE",
    750:  "#0033FF",
    1250: "#DD77FF",
    2000: "#A000A0",
    3200: "#FFA000",
    5000: "#FF4400",
    7500: "#CC0000",
    9999: None
}

async def plot_user(user_id, aclient, ctx):
    resp = await aclient.get(f"https://www.mathraining.be/users/{user_id}")
    
    soup = BeautifulSoup(await resp.text(), features='lxml')

    if soup.select_one('div.error'):
        await ctx.channel.send(f"**{user_id}**: Utilisateur introuvable.")
        return 0, 0, 0, 0
    
    resolutions_table = soup.select_one('table.table.middle_aligned')
    
    name = soup.select_one("title").text.replace('| Mathraining', '').strip()

    if not resolutions_table:
        await ctx.channel.send(f"Impossible de se comparer avec **{name}**.")
        return 0, 0, 0, 0

    points = 0

    x = []
    y = []

    for resolution in reversed(resolutions_table.select('tr')):
        exo_pts = resolution.select_one('td').text.replace('+', '').strip()
        if not exo_pts: # exo fondements
            continue
        exo_pts = int(exo_pts)
        date_element = resolution.select('td')[1]
        date_element.select_one('span').replace_with(' ' + date_element.select_one('span').text)
        date = resolution.select('td')[1].text.strip()
        when = datetime.datetime.strptime(date.replace('h', ':'), '%d/%m/%y %H:%M').date()
        points += exo_pts
        if when in x:
            y[-1] += exo_pts
        else:
            x.append(when)
            y.append(points)
    
    if not x: # 0 points
        await ctx.channel.send(f"Impossible de se comparer avec **{name}**.")
        return 0, 0, 0, 0
    
    x.insert(0, x[0])
    y.insert(0, 0)

    return x, y, name, points

async def make_graph(ctx, id1, id2, aclient):
    async with ctx.channel.typing():
        x, y, name, pts = await plot_user(id1, aclient, ctx)
        if not x: return # if error

        x2, y2, name2, pts2 = await plot_user(id2, aclient, ctx)
        if not x2: return
        
        fig, ax = plt.subplots(figsize=(9,5))
        
        ax.plot(x, y, color='white', linewidth=2, marker='o', markersize=4)
        ax.plot(x2, y2, color='yellow', linewidth=2, marker='o', markersize=4)

        levels_pts = list(MT_LEVELS.keys())
        levels_colors = list(MT_LEVELS.values())
        for i in range(len(MT_LEVELS)-1):
            ax.axhspan(levels_pts[i], levels_pts[i+1], alpha=1, color=levels_colors[i])

        if y[-1] > 5000 or y2[-1] > 5000:
            levels_pts.remove(0)
            levels_pts.remove(200)
        plt.yticks(levels_pts[:-1], levels_pts[:-1])

        ax.set_xlim(min(x[0], x2[0]), max(x[-1], x2[-1]))
        ax.set_ylim(0, int(max(y[-1], y2[-1]) * 1.2))

        ax.legend([name, name2], loc=2)

        plt.margins(y=0)
        fig.tight_layout()
        plt.savefig("compare.png")

        file = File("compare.png")
        embed = Embed(title=f'**{name} ({pts})** vs **{name2} ({pts2})**', color=0x87CEEB)
        embed.set_image(url="attachment://compare.png")
        await ctx.send(file=file, embed=embed)
