# Changed from node:18-alpine to node:20-alpine
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm cache clean --force
RUN npm install --legacy-peer-deps

COPY . .

# Now this will work because Node.js is >= 20.9.0
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]