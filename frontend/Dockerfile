FROM node:20-alpine AS builder

WORKDIR /app

# Set Node.js memory limit to 768MB (leaving some memory for the system)
ENV NODE_OPTIONS="--max-old-space-size=768"

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

#---

FROM node:20-alpine

RUN npm install -g serve

WORKDIR /app

COPY --from=builder /app/build ./build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]