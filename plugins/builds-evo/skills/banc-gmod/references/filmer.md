# Filmer dans GMod (fin de build seulement)

Pendant le maquettage, Adrien veut des images, jamais de film ni de MP4.

- `startmovie` lancé depuis Lua n'écrit rien ; une capture d'écran ffmpeg (`gdigrab`) filme le bureau.
- Ce qui marche : `video.Record` (webm VP8 + Vorbis, 30 i/s, `lockfps`, `SetRecordSound(true)`), `AddFrame` dans `PostRender`, `Finish` à la fin ; caméra scriptée en `CalcView` ; `HUDShouldDraw` à false, `r_drawviewmodel 0`, `cl_drawhud 0`, pas de réticule. Le fichier sort dans `garrysmod\videos\`.
- Puis ffmpeg vers MP4 H.264 + AAC 1920 × 1080 (dans le conteneur : la conversion sur le PC dépasse 3 min), contrôle de la durée (`ffprobe`), du son (`volumedetect`) et de quelques images.
- Focus : GMod reste en arrière-plan ; premier plan seulement pendant la prise, prévenir juste avant, rendre juste après, puis nettoyer la map.
- Le mode côte à côte libère le curseur (`gui.EnableScreenClicker(true)`) : pour filmer, le rendre à la caméra.
- Addon de référence : `sites\azeno\film\azeno_cine\lua\autorun\azeno_cine.lua`.
- Règles de cadrage : skill `mise-en-scene` (`cinema-entrees.md`).
