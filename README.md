Teen Patti Multiplayer Web App

A full-stack multiplayer card game inspired by Teen Patti built using Django, PostgreSQL, TailwindCSS + DaisyUI, Docker, and Bun + uv for frontend build tooling.

⚙️ Installation Guide (Full Setup)

🔹 1. Clone the repo:

git clone https://github.com/SamirShah44/WebDevFinal.git

cd WebDevFinal

🔹 2. Create .env file

Copy and modify the environment variables:


# Postgres
POSTGRES_USER=YOUR_NAME_HERE
POSTGRES_PASSWORD=PASSWORD
POSTGRES_DB=DATABASE_NAME
DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}"

# This is our DEVELOPMENT environment file

# General
DEBUG=1

# Django
DJANGO_ALLOWED_HOSTS="*"
DJANGO_SECRET_KEY=SECURITY_KEY_HERE
DJANGO_TIME_ZONE=America/Chicago

AUTH0_DOMAIN=your-auth0-domain
AUTH0_CLIENT_ID=your-auth0-client-id
AUTH0_CLIENT_SECRET=your-auth0-client-secret

Edit .env and add your Auth0, Postgres, and Django credentials.

🔹 3. Install uv and unzip

✅ For WSL/Linux:

sudo apt update && sudo apt upgrade -y
sudo apt install -y pipx unzip curl
pipx ensurepath
source ~/.bashrc
pipx install uv

✅ For Windows (outside WSL):

python -m pip install --user pipx
python -m pipx ensurepath
pipx install uv

Close and reopen terminal if needed.

🔹 4. Install bun

✅ For WSL/Linux:

curl -fsSL https://bun.sh/install | bash
source ~/.bashrc

Then:

bun install

🔹 5. Build TailwindCSS

bun run watch:css

Make sure output.css appears at:

TeenPatti/static/css/output.css

🔹 6. Install Python Dependencies

uv pip install -r requirements.txt

🔹 7.Setup Auth0

To enable login, each user must create their own Auth0 Application:

Go to Auth0 Dashboard

Create a new Application (Regular Web App)

Add the following URLs:

Allowed Callback URLs:
http://127.0.0.1:8000/complete/auth0,
http://127.0.0.1:8000/login/auth0

Allowed Logout URLs:
http://127.0.0.1:8000/

Allowed Web Origins:
http://127.0.0.1:8000/

Then copy your
Domain
Client ID
Client Secret

And paste them into your local .env file:
AUTH0_DOMAIN=your-auth0-domain
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret

🔹 8. Run Migrations & Start Server

uv run manage.py migrate
uv run manage.py runserver

App will be live at http://127.0.0.1:8000

🐳 Docker Setup (Optional)

🔹 Install Docker (Linux/WSL only)

# Remove old versions
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done


# Install prerequisites
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable Docker for current user
sudo usermod -aG docker $USER

Then restart your terminal and test:

docker ps

🔹 Docker Usage

docker compose up 
Visit : http://127.0.0.1:8000/

Troubleshooting

Auth0 client_id=None?
→ Ensure .env is correctly placed and loaded in settings.py

output.css 404 error?
→ Run bun run watch:css and verify output file exists in static/css/

Docker permission denied?
→ Run sudo usermod -aG docker $USER and restart shell

✨ Authors
Made with ❤️ by Zenish, Surendra, and Samir
