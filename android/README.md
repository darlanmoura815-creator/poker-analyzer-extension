# Poker Ranking Flutuante — Android 1.4

Aplicativo para Android com ranking das mãos de Texas Hold'em e cartas que podem melhorar a combinação. Painel sobreposto, arrastável e minimizável.

**Código-fonte:** [Baixar o projeto Android](poker-ranking-flutuante-v1.4.zip) e extrair no computador. O ZIP contém Java, HTML, JavaScript, CSS, Gradle e recursos locais. O ícone do aplicativo usa recurso vetorial Android, sem dependência de arquivos PNG.

## Gerar o APK pelo GitHub

1. Abra **Actions** no repositório.
2. Entre em **Compilar Poker Ranking Android**.
3. Escolha **Run workflow** (ou abra a execução automática do push).
4. Ao concluir com sucesso, baixe o artifact **Poker-Ranking-Flutuante-APK**.
5. Extraia o artifact para obter `app-debug.apk` e instale no Xiaomi.

O app exige autorização de **Aparecer sobre outros aplicativos**. No Xiaomi: Configurações > Apps > Permissões especiais > Exibir sobre outros apps (o caminho varia por versão). Se a janela não aparecer, verifique se o app ou o sistema bloqueia a sobreposição.

Não faz OCR, captura de tela ou sugestões de apostas. Apenas exibe um guia manual de cartas, probabilidade de melhoria e ranking. Use respeitando as regras do site.

**Nota:** a compilação pelo GitHub Actions precisa ser validada; código e recursos foram conferidos, mas o APK não foi produzido localmente.
