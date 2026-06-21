# Serverless URL Shortener 🔗

A fully serverless URL shortener built with AWS SAM — API Gateway, Lambda, and DynamoDB, deployed entirely as Infrastructure as Code. No servers to manage, no manual console configuration: the whole stack is declared in a single `template.yaml` and deployed with one command.

---

## Architecture

```
                     ┌────────────────────┐
   Client ─────────▶ │    API Gateway     │
   (HTTP)            └─────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
               POST /shorten          GET /{code}
                    │                     │
                    ▼                     ▼
            ┌─────────────────┐   ┌──────────────────┐
            │ create_short_url│   │  redirect_url    │
            └────────┬────────┘   └────────┬─────────┘
                     │                     │
                     └──────────┬──────────┘
                                ▼
                       ┌──────────────────┐
                       │    DynamoDB      │
                       │  ShortenerUrls   │
                       └──────────────────┘
                                ▲
                                │
                        GET /{code}/stats
                                │
                       ┌──────────────────┐
                       │    get_stats     │
                       └──────────────────┘
```

---

## Demo

```bash
$ curl -X POST https://your-api.execute-api.us-east-1.amazonaws.com/Prod/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/jcreyesDev"}'

{"short_code": "6UbkgP", "short_url": "https://your-api.execute-api.us-east-1.amazonaws.com/Prod/6UbkgP", "original_url": "https://github.com/jcreyesDev"}

$ curl https://your-api.execute-api.us-east-1.amazonaws.com/Prod/6UbkgP/stats

{"short_code": "6UbkgP", "original_url": "https://github.com/jcreyesDev", "clicks": 1, "created_at": "2026-06-21T21:10:36.755943+00:00"}
```

---

## Features

- 🔗 Generates short, collision-free codes for any URL (cryptographically secure via `secrets`)
- ↪️ Real HTTP 301 redirects to the original URL
- 📊 Click tracking with atomic increments (race-condition safe)
- 🏗️ Infrastructure as Code — entire stack defined in `template.yaml`, deployed via AWS SAM
- 🔐 Least-privilege IAM roles auto-generated per function (`DynamoDBCrudPolicy`)
- ⚡ Fully serverless — zero server management, scales automatically
- 💰 Runs entirely within AWS Free Tier

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/shorten` | Creates a short URL from a long URL |
| `GET` | `/{code}` | Redirects to the original URL (HTTP 301) and increments click count |
| `GET` | `/{code}/stats` | Returns click count and creation date for a short code |

---

## Project Structure

```
ServerlessUrlShortener/
├── src/
│   ├── create_short_url/
│   │   ├── app.py              # Generates short code, saves to DynamoDB
│   │   └── requirements.txt
│   ├── redirect_url/
│   │   ├── app.py              # Looks up code, redirects, increments clicks
│   │   └── requirements.txt
│   └── get_stats/
│       ├── app.py              # Returns click stats for a short code
│       └── requirements.txt
├── events/
│   ├── shorten_event.json      # Sample API Gateway event for POST /shorten
│   └── redirect_event.json     # Sample API Gateway event for GET /{code}
├── template.yaml                # SAM template — declares all AWS resources
├── samconfig.toml               # SAM deployment configuration
└── README.md
```

---

## Tech Stack

| Technology         | Description                                          |
|---------------------|-------------------------------------------------------|
| Python 3.13         | Primary language                                       |
| AWS SAM             | Infrastructure as Code framework                        |
| boto3               | AWS SDK for Python                                      |
| AWS Lambda          | Serverless function execution                            |
| Amazon API Gateway  | HTTP endpoint routing and Lambda proxy integration       |
| Amazon DynamoDB     | NoSQL database for storing short URLs and click counts   |
| AWS CloudFormation  | Underlying deployment engine used by SAM                 |

---

## DynamoDB Table Design

```
Table: ShortenerUrls
Partition Key: short_code (String)

Attributes:
- short_code: "6UbkgP"
- original_url: "https://github.com/jcreyesDev"
- created_at: "2026-06-21T21:10:36.755943+00:00"
- clicks: 1
```

---

## Prerequisites

- Python 3.13+
- AWS CLI v2 installed and configured
- AWS SAM CLI installed (`brew install aws-sam-cli`)
- An IAM user with permissions for CloudFormation, Lambda, API Gateway, DynamoDB, IAM role creation, and S3 (used by SAM for deployment artifacts)

---

## Installation & Deployment

1. Clone the repository:

```bash
git clone https://github.com/jcreyesDev/ServerlessUrlShortener.git
cd ServerlessUrlShortener
```

2. Build the application:

```bash
sam build
```

3. Deploy to AWS (first time, guided):

```bash
sam deploy --guided --profile your-profile-name
```

4. Subsequent deployments:

```bash
sam deploy --profile your-profile-name
```

After deployment, the API base URL is shown in the `Outputs` section of the terminal and in the CloudFormation console.

---

## Usage

```bash
# Create a short URL
curl -X POST https://your-api-url/Prod/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url"}'

# Visit the short URL (redirects automatically)
curl -L https://your-api-url/Prod/{code}

# Get click statistics
curl https://your-api-url/Prod/{code}/stats
```

---

## Local Testing

Sample API Gateway events are provided in the `events/` folder for local testing with Docker:

```bash
sam local invoke CreateShortUrlFunction -e events/shorten_event.json --profile your-profile-name
```

> Requires Docker Desktop installed and running.

---

## Key Design Decisions

- **Atomic click counting** — uses DynamoDB's `ADD` update expression instead of read-then-write, preventing race conditions under concurrent traffic.
- **Collision-safe code generation** — verifies each generated code against DynamoDB before saving, retrying on collision.
- **Cryptographically secure codes** — uses Python's `secrets` module instead of `random`, ensuring codes are not predictable.
- **Auto-generated least-privilege IAM roles** — SAM's `DynamoDBCrudPolicy` grants each Lambda function access only to the specific table it needs, with zero manual IAM configuration.

---

## Requirements

- Python 3.13+
- AWS CLI v2
- AWS SAM CLI
- Active AWS account

---

## Author

Developed by [@jcreyesDev](https://github.com/jcreyesDev)