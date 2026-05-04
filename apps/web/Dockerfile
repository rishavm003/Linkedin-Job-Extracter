FROM node:22-alpine

WORKDIR /app

# Install curl for healthcheck
RUN apk add --no-cache curl

# Copy pre-built standalone assets from host
# Note: Requires 'npm run build' to have been run on host
COPY apps/web/public ./public
COPY apps/web/.next/standalone ./
COPY apps/web/.next/static ./.next/static

# Set environment variable
ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:3000 || exit 1

# Start the application
CMD ["node", "server.js"]
