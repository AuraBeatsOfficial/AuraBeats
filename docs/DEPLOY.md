# Deployment

## Termux
pkg install python git ffmpeg -y
pip install -r requirements.txt
python AuraBeats

## Docker
docker compose up -d --build

## Heroku/Render
Procfile included: worker: python AuraBeats
