# cicd-assignment-<RollNumber>

Cloud Computing – Lab Assignment 3: CI/CD pipeline with Docker, Selenium and Jenkins.

```
index.html              web page (name, roll no, button, text box + submit)
Dockerfile              nginx image that serves the page
tests/Dockerfile        Selenium test agent (Python, pytest, Chromium, ChromeDriver)
tests/test_site.py      4 Selenium tests (title, heading, button click, text box)
Jenkinsfile             Checkout → Package → Start Staging → Test → Deploy
jenkins/                Jenkins server with Docker CLI (docker compose)
```

---

## 0. Personalise (do this first)

Replace the placeholders in **both** files. If they don't match, the tests fail.

| File | Replace |
|---|---|
| `index.html` | `Your Name` (in `<title>` and `<h1>`), `SP23-BCT-000` |
| `tests/test_site.py` | `STUDENT_NAME`, `ROLL_NUMBER` |

Prerequisites: Docker Desktop (or Docker Engine), Git, and a GitHub account.

---

## Lab Task 1: run the tests manually in the test-agent container

Run these from the repo root:

```bash
docker network create cicd-net
docker build -t cicd-site .
docker run -d --name site-staging --network cicd-net cicd-site

docker build -t cicd-site-tests tests
docker run --name site-tests --network cicd-net -e BASE_URL=http://site-staging cicd-site-tests
```

You should see **4 passed**. 📸 Screenshot this output.

Get the Selenium screenshot that the test saved:

```bash
docker cp site-tests:/tests/results/textbox_test.png .
docker rm -f site-tests site-staging
```

📸 Put `textbox_test.png` in the report.

Then push to GitHub. The repo must be **public** and named `cicd-assignment-<RollNumber>`:

```bash
git init && git add . && git commit -m "Initial CI/CD assignment"
git branch -M main
git remote add origin https://github.com/<you>/cicd-assignment-<RollNumber>.git
git push -u origin main
```

---

## Lab Task 2: Jenkins pipeline

### 2.1 Start Jenkins (with Docker access)

```bash
cd jenkins
docker compose up -d --build
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Open http://localhost:8080, paste the password, choose **Install suggested plugins**, and create an admin user.
The Git, Pipeline, JUnit, GitHub and Stage View plugins are already baked into the image.

Check that Jenkins can reach Docker: run `docker exec jenkins docker ps`. It should list containers.

### 2.2 Create the pipeline job

1. **New Item** → name `cicd-assignment` → **Pipeline** → OK
2. **Triggers**: tick **GitHub hook trigger for GITScm polling**
3. **Pipeline** → Definition: **Pipeline script from SCM** → SCM: **Git**
   - Repository URL: `https://github.com/<you>/cicd-assignment-<RollNumber>.git` (public, so no credentials needed)
   - Branch: `*/main` · Script Path: `Jenkinsfile`
4. Save → **Build Now**. Repeat until all stages are green.

Open **http://localhost:8081**. That's the deployed site.
📸 Take screenshots of the Jenkinsfile, the green Stage View, and the live site.

### 2.3 Quality gate demo (failed test, Deploy skipped)

1. In `index.html` change `pipeline is working` → `pipeline is BROKEN`. Commit and push, or click Build Now.
2. **Test** goes red, **Deploy** is skipped, and http://localhost:8081 still shows the old page.
   📸 Take screenshots of the Stage View (red Test, skipped Deploy) and the unchanged live site.
3. Revert the text, push, and confirm the pipeline is green again.

### 2.4 GitHub webhook (push starts the build automatically)

GitHub can't reach `localhost`, so expose Jenkins with ngrok:

```bash
ngrok http 8080
```

Copy the `https://xxxx.ngrok-free.app` URL.

- In Jenkins: **Manage Jenkins → System → Jenkins URL**, set it to the ngrok URL.
- In the GitHub repo: **Settings → Webhooks → Add webhook**
  - Payload URL: `https://xxxx.ngrok-free.app/github-webhook/` (the trailing slash matters)
  - Content type: `application/json` · Event: **Just the push event** → Add

Make a small text change, commit and push. **Do not click Build Now.** A build should start by itself and show
"Started by GitHub push by …" in its console output.
📸 Screenshot the build page and the green tick on the webhook's Recent Deliveries.

### 2.5 Review at least 3 builds

For 3 builds, open each of these:

- the **Test Result** page (4 tests, pass/fail),
- the **Console Output**,
- the **Stage View** timings (how long each stage took).

The saved Selenium screenshot is also attached to each build under **Build Artifacts**.

---

## Report checklist: `LastName_RollNumber_Assignment3.pdf`

1. Page 1: GitHub repository URL
2. Jenkinsfile screenshot
3. Manual test run (Task 1), showing 4 passed, plus the Selenium screenshot
4. Stage View, all green
5. Failed run: Test red, Deploy skipped, live site unchanged
6. Webhook-triggered build ("Started by GitHub push")
7. Test Result page
8. Live site showing your name
9. (Optional) a table of stage timings for 3 builds

**Hide any tokens or passwords** in the screenshots, including the Jenkins admin password and the ngrok authtoken.
Keep Jenkins and Docker running until the viva: `docker compose up -d` in `jenkins/` brings Jenkins back.

---

## Viva notes

- **Why a staging container?** Tests run against the exact image that will be deployed, on a private Docker network (`cicd-net`). Production is only touched if the tests pass.
- **Quality gate:** the Test stage exits with pytest's exit code. A non-zero code fails the stage, so Jenkins skips Deploy.
- **How do results reach Jenkins?** pytest writes JUnit XML (`--junitxml`). The pipeline `docker cp`s it out of the test container, and the `junit` step publishes it. This runs in `post { always }`, so you still get results when tests fail.
- **Why the `docker.sock` mount?** Jenkins uses the host's Docker engine, so the containers it creates are siblings of Jenkins, not nested inside it. That's why the site appears on host port 8081.
- **Webhook flow:** git push → GitHub POSTs to `/github-webhook/` → the GitHub plugin matches the repo URL → the job starts. The `triggers { githubPush() }` block registers the trigger after the first build.
- **Why headless Chromium?** A container has no display, so Chrome runs headless. `--no-sandbox` and `--disable-dev-shm-usage` are needed inside Docker.
- **`skipDefaultCheckout()`:** stops Jenkins doing a hidden checkout, so the explicit Checkout stage is the one that runs.
