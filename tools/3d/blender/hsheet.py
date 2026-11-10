from PIL import Image,ImageDraw,ImageFont
import os,sys;D=os.path.dirname(os.path.abspath(__file__));m=sys.argv[1]
f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',22);o=Image.new('RGB',(3*580+20,2*660+20),'#f3f0f5');d=ImageDraw.Draw(o)
for i,(n,l) in enumerate([('front','정면'),('f34','앞 3/4'),('side','측면'),('back','후면'),('b34','뒤 3/4'),('top','위')]):
    im=Image.open(D+'/hr_%s_%s.png'%(m,n)).convert('RGB');x=20+(i%3)*580;y=20+(i//3)*660;mk=Image.new('L',im.size,0);ImageDraw.Draw(mk).rounded_rectangle((0,0,559,639),24,fill=255);o.paste(im,(x,y),mk)
    tw=d.textlength(l,font=f)+30;d.rounded_rectangle((x+280-tw/2,y+590,x+280+tw/2,y+624),17,fill='#1d2836');d.text((x+280,y+607),l,font=f,fill='#fff',anchor='mm')
o.save(D+'/hair_%s.png'%m)
