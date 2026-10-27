#!/bin/bash
# Records Fragment Reveal II (six photos) at 2x and 25 fps into a lossless video.
set -e
cd /tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/scratchpad
node frag3rec.cjs frag4 25
ffmpeg -loglevel error -y -framerate 25 -i frag4/f%04d.png -c:v ffv1 frag4/loop.mkv
find frag4 -maxdepth 1 -name 'f*.png' -delete
echo RECORDED
