FROM node:18-alpine

WORKDIR /app

# Copy package files first
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy the rest of the application
COPY . .

EXPOSE 3000

# Run in dev mode with hot reloading
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
