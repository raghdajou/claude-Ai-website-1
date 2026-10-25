#!/bin/bash
# Record one photo version at 2x and 33.3 fps (GIF delay of exactly 3 cs), close the loop with the
# same crossfade as before, then write a 2800 MP4 and a high-quality 1400 GIF.
set -e
S=/tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/scratchpad
E=/home/user/claude-Ai-website-1/behance-codigo/exports
n=$1; L=7.92; F=0.8; FPS=33.333333
XF="split[s1][s2];[s1]trim=$F:$(echo "$L+$F" | bc),setpts=PTS-STARTPTS[x];[s2]trim=0:$F,setpts=PTS-STARTPTS[y];[x][y]xfade=transition=fade:duration=$F:offset=$(echo "$L-$F" | bc)"
D=$S/bgframes/$n; rm -rf $D; mkdir -p $D
cd $S && Q=bg=$n EXTRA=$F node cdrec.cjs $D 0 0 $FPS | tail -1
ffmpeg -loglevel error -y -framerate 100/3 -i $D/f%04d.png -filter_complex "[0]$XF" -c:v ffv1 $D/loop.mkv
ffmpeg -loglevel error -y -i $D/loop.mkv -vf format=yuv420p -c:v libx264 -crf 12 -preset slow -tune animation -movflags +faststart $E/ai-chat-prompt-bg$n-2800x1576.mp4
echo "recorded $n"
