from discord import *
from discord.ext import commands
from discord.utils import get

from asyncio import *

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from re import findall
from io import BytesIO

options = webdriver.FirefoxOptions()
options.add_argument('-headless')

async def aopscore(bot,ctx) :
        driver = webdriver.Firefox(options=options)
        #driver = webdriver.PhantomJS(executable_path=r'B:\downloads\MT\PJS\bin\phantomjs.exe')
        #driver.set_window_position(-2000,0)
        #driver.set_window_size(2560, 1600)
        #driver.execute_script("document.body.style.zoom='250%'")
        #driver.execute_script("document.body.style.webkitTransform = 'scale(1.5)'")
        #driver.implicitly_wait(10)
        urlinit="https://artofproblemsolving.com/community/c13_contest_collections";url=urlinit
        msg = await bot.say("`Chargement en cours ...`")
        driver.get(url);await sleep(2)
        titres = [(i.text).split('\n')+['\u200b']*(2-len((i.text).split('\n'))) for i in driver.find_elements_by_class_name('cmty-category-cell-left') if i.text != '']
        titre=titres[0][0];titres=titres[1:];l=len(titres);k=0
        reactions=["🔙","◀","▶","1⃣","2⃣","3⃣","4⃣","5⃣","6⃣","7⃣","8⃣","9⃣","🔟","❌"]
        while l :
            embed = Embed(title=titre, colour=0x009fad)
            liens =[i.find_element_by_css_selector('a').get_attribute('href') for i in driver.find_elements_by_class_name('cmty-category-cell-heading.cmty-cat-cell-top-legit')]
            embed.set_footer(text="AoPS | Page "+str(k+1)+"/"+str((l-1)//10 +1)+" | Attendez que les réactions soient toutes présentes.")
            for i in range(k*10,k*10+min(10,len(titres)-k*10)) : embed.add_field(name=str(i+1)+'. '+titres[i][0],value=titres[i][1],inline=False)
            await bot.edit_message(msg,embed=embed)
            await bot.edit_message(msg,"`Veuillez faire une sélection :`")
            for r in reactions[:min(10,l-k*10)+3]+["❌"]*(10!=(l-k*10)) : await bot.add_reaction(msg,r)
            reac = await bot.wait_for_reaction(reactions,message=msg,user=ctx.message.author,timeout=60)
            if reac :
                await bot.edit_message(msg,"`Chargement en cours ...`")
                await bot.clear_reactions(msg)
                for i in range(min(10,len(titres)-k*10)+3) :
                    if reac.reaction.emoji == "❌" :
                        await bot.edit_message(msg,"`La requête a été annulée.`")
                        await bot.clear_reactions(msg)
                        await bot.edit_message(msg,embed=Embed(title='AoPS | Terminé', colour=0x009fad))
                        driver.quit();return
                    if reac.reaction.emoji == reactions[1] and k!=0 :
                        k-=1;break
                    if reac.reaction.emoji == reactions[2] and k<((l-1)//10) :
                        k+=1;break
                    if reac.reaction.emoji == reactions[i] and reac.reaction.emoji not in reactions[1:3] :
                        if reac.reaction.emoji == reactions[0] :
                            if not url==urlinit :
                                driver.back();url=driver.current_url
                            else : break
                        else : url = liens[k*10+i-3];driver.get(url)
                        await sleep(2)
                        last_height = driver.execute_script("return document.body.scrollHeight")
                        while True: #CHARGER LA PAGE ENTIEREMENT EN SCROLLANT !!
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            await sleep(0.3);new_height = driver.execute_script("return document.body.scrollHeight")
                            if new_height == last_height: break
                            last_height = new_height
                        titres = [(i.text).split('\n')+['\u200b']*(2-len((i.text).split('\n'))) for i in driver.find_elements_by_class_name('cmty-category-cell-left') if i.text != '']
                        titre=titres[0][0];titres=titres[1:len(titres)-1*(url==urlinit)];l=len(titres);k=0 #Si url = urlinit on enlève le dernier pathologique
                        break
            else :
                await bot.edit_message(msg,"`Aucune réponse depuis une minute. La requête a été abandonnée.`")
                await bot.clear_reactions(msg)
                await bot.edit_message(msg,embed=Embed(title='AoPS | Terminé', colour=0x009fad))
                driver.quit();return
        driver.execute_script("window.scrollTo(0, 0);")
        #re.findall("\d+", 'Problem 10')
        #https://artofproblemsolving.com/community/c389682_2016_china_second_round_olympiad ??????
        #https://artofproblemsolving.com/community/c502938_2017_middle_european_mathematical_olympiad :(
        #https://artofproblemsolving.com/community/c930482_2005_dutch_mathematical_olympiad
        #https://artofproblemsolving.com/community/c681585_2018_imo
        DescsParties = [(lambda x : '\u200b' if x==[] else x[0].text)(i.find_elements_by_class_name('cmty-view-post-item-text')) for i in driver.find_elements_by_class_name('cmty-view-posts-item') if i.find_elements_by_class_name('cmty-view-post-poster') == []]

        NumsParties = [(lambda x : '\u200b' if x==[] else x[0].text)(i.find_elements_by_class_name('cmty-view-post-item-label')) for i in driver.find_elements_by_class_name('cmty-view-posts-item') if i.find_elements_by_class_name('cmty-view-post-poster') == []]
        #Nums = [(lambda x : '\u200b' if x==[] else x[0].text)(i.find_elements_by_class_name('cmty-view-post-item-label')) for i in driver.find_elements_by_class_name('cmty-view-posts-item') if i.find_elements_by_class_name('cmty-view-post-poster') != []]

        LesNums = [[(lambda x : '\u200b' if x==[] else findall("\d+",x[0].text)[0])(i.find_elements_by_class_name('cmty-view-post-item-label')),i.find_elements_by_class_name('cmty-view-post-poster') == []] for i in driver.find_elements_by_class_name('cmty-view-posts-item')]  #True ssi Partie
        LesNums = list(filter(lambda x: x != ['\u200b', False], LesNums))

        Probs = [i.find_elements_by_class_name('cmty-view-post-item-text')[0] for i in driver.find_elements_by_class_name('cmty-view-posts-item') if i.text != '' and i.find_elements_by_class_name('cmty-view-post-item-label') != [] and i.find_elements_by_class_name('cmty-view-post-poster') != []]
        #OtherProbs = [i.find_elements_by_class_name('cmty-view-post-item-text')[0] for i in driver.find_elements_by_class_name('cmty-view-posts-item') if i.text != '' and i.find_elements_by_class_name('cmty-view-post-item-label') == [] and i.find_elements_by_class_name('cmty-view-post-poster') != []]

        PartiesPos = [i for i in range(len(LesNums)) if LesNums[i][1] == True];PartiesPos+=[len(LesNums)]
        selec=["_","_","_"]
        reactions2=["0⃣","1⃣","2⃣","3⃣","4⃣","5⃣","6⃣","7⃣","8⃣","9⃣","✳","✅","❌"]
        prob=await bot.say("`Le problème apparaîtra ici.`")
        while reac.reaction.emoji != reactions2[-1] :
            embed = Embed(title=titre+" | Votre sélection actuelle : "+selec[0]+"-"+selec[1]+selec[2],colour=0x009fad)
            embed.set_footer(text="AoPS | Attendez que les réactions soient toutes présentes.")
            for i in range(len(NumsParties)) :
                nbrs=''
                for j in range(1,PartiesPos[i+1]-PartiesPos[i]) : nbrs+=LesNums[PartiesPos[i]+j][0]+' - '
                embed.add_field(name="__"+str(i+1)+".__ `"+str(NumsParties[i])+"` _"+str(DescsParties[i])+"_",value=nbrs[:-3],inline=False)
            await bot.edit_message(msg,embed=embed)
            await bot.edit_message(msg,"`Veuillez faire une sélection :`")
            for r in reactions2 : await bot.add_reaction(msg,r)
            reac = await bot.wait_for_reaction(reactions2,message=msg,user=ctx.message.author,timeout=5*60)
            if reac :
                await bot.edit_message(msg,"`Chargement en cours ...`")
                await bot.clear_reactions(msg)
                for i in range(len(reactions2)-1) :
                    if reac.reaction.emoji == reactions2[10] : selec=['_','_','_'];break
                    if reac.reaction.emoji == reactions2[11] and '_' not in selec :
                        try :
                            img=BytesIO((Probs[PartiesPos[int(selec[0])-1]-int(selec[0])+int(selec[1]+selec[2])]).screenshot_as_png);img.name='problem.png'
                            #f = open('mt1.png', 'wb')
                            #f.write(Probs[5].screenshot_as_png)
                            #f.close()
                            await bot.delete_message(prob)
                            prob=await bot.send_file(ctx.message.channel, img)
                            break
                        except : bot.edit_message(prob,"`Sélection invalide !`")
                    if reac.reaction.emoji == reactions2[i] and '_' in selec and i<10 :
                        if selec[0] == '_' : selec[0] = str(i)
                        elif selec[1] == '_' : selec[1] = str(i)
                        else : selec[2] = str(i)
                        break
            else :
                await bot.edit_message(msg,"`Aucune réponse depuis cinq minutes. La requête a été abandonnée.`")
                await bot.clear_reactions(msg)
                await bot.edit_message(msg,embed=Embed(title='AoPS | Terminé', colour=0x009fad))
                driver.quit();return

        await bot.edit_message(msg,"`La requête a été terminée.`")
        await bot.clear_reactions(msg)
        await bot.edit_message(msg,embed=Embed(title='AoPS | Terminé', colour=0x009fad))
        driver.quit()