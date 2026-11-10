from PIL import Image,ImageDraw,ImageFont
import os;D=os.path.dirname(os.path.abspath(__file__));k=Image.open(D+'/h_hero.png').size[0]/930
W,H=int(2600*k),int(1560*k);o=Image.new('RGB',(W,H),'#f3f0f5');d=ImageDraw.Draw(o);f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',int(26*k)) if os.path.exists('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc') else ImageFont.load_default()
for n,x,y,l in [('hero',30,30,''),('front',990,30,'FRONT'),('side',1530,30,'SIDE'),('back',2070,30,'BACK'),('face',990,795,'얼굴'),('acc',1530,795,'머리 장식'),('back34',2070,795,'뒤 3/4')]:
    im=Image.open(D+'/h_%s.png'%n).convert('RGB');m=Image.new('L',im.size,0);ImageDraw.Draw(m).rounded_rectangle((0,0,im.size[0]-1,im.size[1]-1),int(28*k),fill=255);o.paste(im,(int(x*k),int(y*k)),m)
    if l:
        tw=d.textlength(l,font=f)+36*k;cx=int(x*k)+im.size[0]/2;by=int(y*k)+im.size[1]-58*k;d.rounded_rectangle((cx-tw/2,by,cx+tw/2,by+40*k),int(20*k),fill='#1d2836');d.text((cx,by+20*k),l,font=f,fill='#fff',anchor='mm')
o.save(D+'/hero_bl.png')
