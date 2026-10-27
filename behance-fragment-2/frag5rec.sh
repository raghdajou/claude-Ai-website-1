#!/bin/bash
# Records Fragment Reveal II (six photos) at 2x and 20 fps into a lossless video.
set -e
cd /tmp/claude-0/-home-user-claude-Ai-website-1/fd49522e-f0ff-52ed-b6c7-08cca43cc4fd/scratchpad
node frag3rec.cjs frag5 20
ffmpeg -loglevel error -y -framerate 20 -i frag5/f%04d.png -c:v ffv1 frag5/loop.mkv
find frag5 -maxdepth 1 -name 'f*.png' -delete
echo RECORDED
