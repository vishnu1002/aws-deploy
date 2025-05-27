# Stage 1: Build the React app
FROM node:18 AS builder

# Set working directory
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the code and build
COPY . .
RUN npm run build

# Stage 2: Serve the built app with a lightweight web server (e.g., nginx or serve)
FROM node:18-slim

# Install a simple HTTP server to serve static files
RUN npm install -g serve

# Set working directory
WORKDIR /app

# Copy build artifacts from the builder stage
COPY --from=builder /app/build ./build

# Expose port
EXPOSE 3000

# Command to run the app
CMD ["serve", "-s", "build", "-l", "3000"]
