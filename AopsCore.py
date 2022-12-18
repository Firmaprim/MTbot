from discord import *
from discord.ext import commands
from discord.utils import get

from asyncio import *
from asyncio import subprocess

from re import findall, compile
import json, datetime, math, os
from bs4 import BeautifulSoup
from traceback import format_exc

NUM_ITEMS_PAGE = 10
MAX_LIMIT = 500

clients, cache = {}, {}

async def fetch_session():
    page = await (await aclient.get("https://artofproblemsolving.com/community/c13")).text()
    script = BeautifulSoup(page, 'lxml').find_all("script")[2].decode_contents()
    session = json.loads(compile(r"AoPS\.session *= *(\{.*?\});").findall(script)[0])
    return session

async def fetch_category(item_id, session, interaction=None):
    if item_id not in cache:
        #print(f"AoPS: Fetching category {item_id}")
        response = await aclient.post("https://artofproblemsolving.com/m/community/ajax.php", data={
            'category_id': f"{item_id}",
            'a': "fetch_category_data",
            'aops_logged_in': session['logged_in'],
            'aops_user_id': session['user_id'],
            'aops_session_id': session['id'],
        })
        obj = json.loads(await response.text())['response']['category']

        while not obj['no_more_items'] and len(obj['items']) < MAX_LIMIT:
            if interaction and not interaction.response.is_done(): await interaction.response.defer()
            #print(f"AoPS: Fetching more items from category {item_id}")
            response = await aclient.post("https://artofproblemsolving.com/m/community/ajax.php", data={
                'category_id': f"{item_id}",
                'last_item_score': obj.get('last_item_score'),
                'last_item_level': obj.get('last_item_level'),
                'last_item_text': obj.get('last_item_text'),
                'start_num': len(obj['items']),
                'fetch_all': "0",
                'a': "fetch_more_items",
                'aops_logged_in': session['logged_in'],
                'aops_user_id': session['user_id'],
                'aops_session_id': session['id'],
            })
            new_obj = json.loads(await response.text())['response']

            obj['items'] += new_obj['items'][1:]
            for i in ('no_more_items', 'last_item_text', 'last_item_score', 'last_item_level'):
                if i in new_obj: obj[i] = new_obj[i]
                elif i in obj and i not in new_obj: del obj[i]

        cache[item_id] = obj
    return cache[item_id]

async def aopscore(bot, ctx, _aclient):
    global aclient; aclient = _aclient
    async with ctx.channel.typing():
        session = await fetch_session()
        client = {
            'user_id': ctx.author.id,
            'path': [13],
            'last_activity': datetime.datetime.now(),
            'page': [0],
            'message': ctx,
            'session': session,
            'showed_pbs': {}
        }
        msg = await update_message(client)
        client['message'] = msg
        clients[msg.id] = client

async def update_message(client, interaction=None):
    cat_id = client['path'][-1]
    category = await fetch_category(cat_id, client['session'], interaction)

    folders = [item for item in category['items'] if item['item_type'].startswith("folder") or item['item_type'] in ('view_posts')]

    page = client['page'][-1]
    num_pages = math.ceil(len(folders) / NUM_ITEMS_PAGE)

    showed_folders = folders[page*NUM_ITEMS_PAGE : (page+1)*NUM_ITEMS_PAGE]

    embed = Embed(title=category['category_name'], color=0x009fad, url=f"https://artofproblemsolving.com/community/c{cat_id}")
    embed.set_footer(text=f"AoPS | Page {page+1}/{num_pages}")

    view = ui.View()
    p = NUM_ITEMS_PAGE * page + 1

    thelist1, thelist2 = [], []

    for item in showed_folders:
        if item['item_type'] == 'post':
            if item['post_data']['post_type'] == 'view_posts_text':
                thelist1.append(f"{item['item_text']}")
                thelist2.append("")
            elif item['item_text']:
                text = item['post_data']['post_canonical'].replace("\r\n", " ")
                if len(text) > 89: text = text[:89] + "…" # total size of field value must be < 1024

                if thelist2 == []: thelist1.append(""); thelist2.append("")
                thelist2[-1] += f"**{item['item_text']}** {text}\n"

                view.add_item(ui.Button(style=ButtonStyle.primary, label=item['item_text'], custom_id=f"aops-problem-{cat_id}-{item['item_id']}"))
                p += 1
        else:
            embed.add_field(name=f"{p}. {item['item_text']}", value=item['item_subtitle'] or "\u200b", inline=True)
            view.add_item(ui.Button(style=ButtonStyle.primary, label=f"{p}", custom_id=f"aops-collection-{item['item_id']}"))
            p += 1

    for a, b in zip(thelist1, thelist2):
        embed.add_field(name=a or "\u200b", value=b or "\u200b", inline=False)

    view.add_item(ui.Button(row=4, style=ButtonStyle.success, emoji="🔙", custom_id=f"aops-back", disabled=len(client['path']) == 1))
    view.add_item(ui.Button(row=4, style=ButtonStyle.success, emoji="◀", label="Précédent", custom_id=f"aops-prev", disabled=page == 0))
    view.add_item(ui.Button(row=4, style=ButtonStyle.success, emoji="▶", label="Suivant", custom_id=f"aops-next", disabled=page == num_pages-1))
    view.add_item(ui.Button(row=4, style=ButtonStyle.danger, emoji="❌", custom_id=f"aops-cancel"))

    if interaction:
        if interaction.response.is_done():
            await interaction.followup.edit_message(client['message'].id, embed=embed, view=view)
        else:
            await interaction.response.edit_message(embed=embed, view=view)
    else:
        return await client['message'].send(embed=embed, view=view)

async def process_click(interaction, _aclient):
    global aclient; aclient = _aclient
    if interaction.message.id not in clients:
        await interaction.response.edit_message(content="`Aucune réponse depuis 15 minutes. La requête a été abandonnée.`", embed=Embed(title='AoPS | Terminé', colour=0x009fad), view=ui.View())
        return
    client = clients[interaction.message.id]
    if interaction.user.id != client['user_id']:
        await interaction.response.send_message(ephemeral=True, content=f"Seul <@!{client['user_id']}> peut utiliser cette instance.")
        return

    action = interaction.data['custom_id'][5:]
    client['last_activity'] = datetime.datetime.now()

    if action.startswith('collection-'):
        item_id = int(action.replace('collection-', ''))
        client['path'].append(item_id)
        client['page'].append(0)
        await update_message(client, interaction)

    elif action.startswith('problem-'):
        cat_id, item_id = map(int, action.replace('problem-', '').split('-'))

        if item_id in client['showed_pbs']:
            await interaction.response.defer()
            try:
                await client['showed_pbs'][item_id].delete()
            except (NotFound, AttributeError): pass
            del client['showed_pbs'][item_id]
            return

        await interaction.response.defer(thinking=True)

        cat = await fetch_category(cat_id, client['session'])
        sub_cat_name = ""
        for i in cat['items']:
            if i['post_data']['post_type'] == 'view_posts_text':
                sub_cat_name = f" ▹ {i['item_text']}" if i['item_text'] else ""
            elif i['item_id'] == item_id:
                problem = i; break

        if not os.path.isdir('tmp/'): os.mkdir('tmp')

        if not os.path.exists(f"tmp/aops-{item_id}.png"):
            with open(f"tmp/aops-{item_id}.html", "w") as file:
                file.write("<style>body{zoom: 200%;}img.latexcenter{display:block;margin:auto;padding:1em 0;height:auto;}</style>")
                file.write(problem['post_data']['post_rendered'].replace("\"//", "\"https://"))
            process = await create_subprocess_exec("wkhtmltoimage", "--quality", "1", "--disable-javascript", f"tmp/aops-{item_id}.html", f"tmp/aops-{item_id}.png")
            await process.communicate()
            os.remove(f"tmp/aops-{item_id}.html")

        embed = Embed(title=f"{cat['category_name']}{sub_cat_name} ▹ {problem['item_text']}", color=0x009fad, url=f"https://artofproblemsolving.com/community/c6h{problem['post_data']['topic_id']}p{problem['post_data']['post_id']}")
        embed.set_image(url=f"attachment://aops-{item_id}.png")

        msg = await interaction.followup.send(embed=embed, file=File(f"tmp/aops-{item_id}.png"))

        client['showed_pbs'][item_id] = msg

        #os.remove(f"tmp/aops-{item_id}.png")

    elif action == 'back':
        client['path'].pop()
        client['page'].pop()
        await update_message(client, interaction)

    elif action == 'prev':
        client['page'][-1] -= 1
        await update_message(client, interaction)

    elif action == 'next':
        client['page'][-1] += 1
        await update_message(client, interaction)

    elif action == 'cancel':
        await interaction.response.edit_message(content="`La requête a été terminée.`", embed=Embed(title='AoPS | Terminé', colour=0x009fad), view=ui.View())
        del clients[interaction.message.id]

    else:
        await interaction.response.send_message(content=":warning: Une erreur est survenue.")
        return

async def task(_aclient): # destroy expired clients
    global aclient; aclient = _aclient
    limit = datetime.datetime.now() - datetime.timedelta(minutes=15)
    for msg_id, client in list(clients.items()):
        if client['last_activity'] < limit:
            try:
                await client['message'].edit(content="`Aucune réponse depuis 15 minutes. La requête a été abandonnée.`", embed=Embed(title='AoPS | Terminé', colour=0x009fad), view=ui.View())
                del clients[msg_id]
            except NotFound: pass
