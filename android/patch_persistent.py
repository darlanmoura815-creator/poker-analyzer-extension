#!/usr/bin/env python3
"""Ajusta o projeto Android extraído do ZIP v1.4 para bolha persistente v1.5."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv)>1 else "android-src")
src = root/"app/src/main"
svc = src/"java/br/com/pokerranking/floating/FloatingService.java"
act = src/"java/br/com/pokerranking/floating/MainActivity.java"
manifest = src/"AndroidManifest.xml"
gradle = root/"app/build.gradle"

def change(text, before, after):
    if before not in text:
        raise RuntimeError("Trecho esperado não encontrado: " + before[:90])
    return text.replace(before, after, 1)

s=svc.read_text()
s=change(s,'private static final String CHANNEL="poker_rank_overlay";',
'''private static final String CHANNEL="poker_rank_overlay";
    private static final String ACTION_SHOW="br.com.pokerranking.floating.SHOW";
    private static final String ACTION_CLOSE="br.com.pokerranking.floating.CLOSE";''')
s=change(s,'private LinearLayout root,header;private WebView web;private TextView resize;',
         'private LinearLayout root,content,header;private WebView web;private TextView resize,bubble;')
s=change(s,'root.setBackground(rounded(Color.rgb(14,19,26),12));root.setClipToOutline(true);',
'''root.setBackground(rounded(Color.rgb(14,19,26),12));root.setClipToOutline(true);
        content=new LinearLayout(this);content.setOrientation(LinearLayout.VERTICAL);
        root.addView(content,new LinearLayout.LayoutParams(-1,-1));''')
s=change(s,'root.addView(header,hp);','content.addView(header,hp);')
s=change(s,'root.addView(web,new LinearLayout.LayoutParams(-1,0,1f));','content.addView(web,new LinearLayout.LayoutParams(-1,0,1f));')
s=change(s,'root.addView(resize,new LinearLayout.LayoutParams(-1,dp(24)));','content.addView(resize,new LinearLayout.LayoutParams(-1,dp(24)));')
s=change(s,'        wm.addView(root,params);',
'''        bubble=headerButton("♠");bubble.setTextSize(25);
        bubble.setBackground(rounded(Color.rgb(32,36,43),30));
        bubble.setContentDescription("Abrir Poker Ranking");
        bubble.setVisibility(View.GONE);
        root.addView(bubble,new LinearLayout.LayoutParams(-1,-1));
        bubble.setOnTouchListener(new View.OnTouchListener(){
            float downX,downY;int startX,startY;boolean moved;
            @Override public boolean onTouch(View v,MotionEvent event){
                switch(event.getActionMasked()){
                    case MotionEvent.ACTION_DOWN:
                        downX=event.getRawX();downY=event.getRawY();
                        startX=params.x;startY=params.y;moved=false;return true;
                    case MotionEvent.ACTION_MOVE:
                        int nx=startX+(int)(event.getRawX()-downX);
                        int ny=startY+(int)(event.getRawY()-downY);
                        if(Math.abs(nx-startX)>dp(6)||Math.abs(ny-startY)>dp(6))moved=true;
                        if(moved){params.x=Math.max(0,Math.min(screenW()-params.width,nx));
                            params.y=Math.max(0,Math.min(screenH()-params.height,ny));updateWindow();}
                        return true;
                    case MotionEvent.ACTION_UP:
                        if(!moved)toggleMinimize(minimizeBtn);
                        return true;
                }
                return false;
            }
        });
        wm.addView(root,params);''')
a=s.index('    private void toggleMinimize(')
b=s.index('    private void updateWindow()',a)
s=s[:a]+'''    private void toggleMinimize(TextView btn){
        minimized=!minimized;
        if(minimized){
            content.setVisibility(View.GONE);bubble.setVisibility(View.VISIBLE);
            params.width=dp(56);params.height=dp(56);btn.setText("□");
        }else{
            bubble.setVisibility(View.GONE);content.setVisibility(View.VISIBLE);
            params.width=Math.min(fullWidth,screenW()-dp(10));
            params.height=Math.min(fullHeight,screenH()-dp(60));
            params.x=Math.max(0,Math.min(params.x,screenW()-params.width));
            params.y=Math.max(0,Math.min(params.y,screenH()-params.height));
            btn.setText("−");
        }
        updateWindow();
    }
'''+s[b:]
s=change(s,'        Notification notification=nb.setSmallIcon(R.drawable.ic_notification)',
'''        Intent show=new Intent(this,FloatingService.class).setAction(ACTION_SHOW);
        PendingIntent showPi=PendingIntent.getService(this,1,show,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        Intent close=new Intent(this,FloatingService.class).setAction(ACTION_CLOSE);
        PendingIntent closePi=PendingIntent.getService(this,2,close,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        Notification notification=nb.setSmallIcon(R.drawable.ic_notification)''')
s=change(s,'.setContentText("Painel de consulta ativo. Toque para abrir as opções.")',
         '.setContentText("Bolha ativa. Toque em Mostrar para abrir.")')
s=change(s,'.setOngoing(true).setContentIntent(pi).build();',
'''.setOngoing(true).setContentIntent(pi)
            .addAction(R.drawable.ic_notification,"Mostrar",showPi)
            .addAction(R.drawable.ic_notification,"Encerrar",closePi).build();''')
s=change(s,'    @Override public int onStartCommand(Intent intent,int flags,int startId){return START_STICKY;}',
'''    @Override public int onStartCommand(Intent intent,int flags,int startId){
        if(intent!=null){
            String action=intent.getAction();
            if(ACTION_CLOSE.equals(action)){stopSelf();return START_NOT_STICKY;}
            if(ACTION_SHOW.equals(action)&&minimized&&root!=null)
                toggleMinimize((TextView)header.getChildAt(2));
        }
        return START_STICKY;
    }''')
svc.write_text(s)

s=act.read_text()
s=change(s,'import android.app.Activity;',
           'import android.app.Activity;\nimport android.Manifest;\nimport android.content.pm.PackageManager;')
s=change(s,'            if(Build.VERSION.SDK_INT>=26)startForegroundService(s);else startService(s);',
'''            if(Build.VERSION.SDK_INT>=33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)
                requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},331);
            if(Build.VERSION.SDK_INT>=26)startForegroundService(s);else startService(s);''')
s=change(s,'            Toast.makeText(this,"Painel aberto. Volte ao Chrome para jogar.",Toast.LENGTH_LONG).show();',
'''            Toast.makeText(this,"Bolha ativada. Abra o Brasa Poker.",Toast.LENGTH_LONG).show();
            moveTaskToBack(true);''')
s=change(s,'        action("Abrir Brasa Poker no navegador",page,v->{',
'''        action("3 · Permitir segundo plano no Xiaomi",page,v->{
            Intent i=new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS,Uri.parse("package:"+getPackageName()));
            startActivity(i);
        });
        page.addView(label("No Xiaomi: escolha Bateria → Sem restrições, permita notificações e, se houver, Início automático. Isso reduz os encerramentos, mas não impede todos.",12,Color.rgb(188,196,209),false));
        action("Abrir Brasa Poker no navegador",page,v->{''')
act.write_text(s)

s=manifest.read_text()
s=change(s,'<uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE"/>',
'''<uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE"/>
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>''')
manifest.write_text(s)
s=gradle.read_text()
s=change(s,'versionCode 14','versionCode 15')
s=change(s,"versionName '1.4'","versionName '1.5'")
gradle.write_text(s)
print("Poker Ranking 1.5: bolha persistente, notificação e ajustes Xiaomi aplicados.")
