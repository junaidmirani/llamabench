#!/usr/bin/env python3
"""
Mock inference server for testing llamabench

This simulates an inference engine API endpoint for testing purposes.
Useful when you don't have actual engines running.

Usage:
    python scripts/mock_server.py
    
Then run llamabench against http://localhost:8080
"""

import asyncio
import json
from aiohttp import web
import random
import time


class MockInferenceServer:
    """Mock server that simulates inference engine behavior"""
    
    def __init__(self, port=8080, latency_ms=150, tokens_per_sec=40):
        self.port = port
        self.latency_ms = latency_ms  # Simulated TTFT
        self.tokens_per_sec = tokens_per_sec
        self.request_count = 0
    
    async def health(self, request):
        """Health check endpoint"""
        return web.json_response({"status": "ok"})
    
    async def completion(self, request):
        """Simulated completion endpoint (llama.cpp style)"""
        try:
            data = await request.json()
            prompt = data.get('prompt', '')
            n_predict = data.get('n_predict', 100)
            stream = data.get('stream', False)
            
            # Simulate TTFT
            await asyncio.sleep(self.latency_ms / 1000)
            
            if stream:
                # Streaming response
                response = web.StreamResponse()
                response.headers['Content-Type'] = 'application/json'
                await response.prepare(request)
                
                # Generate tokens
                for i in range(n_predict):
                    chunk = {
                        'content': f'token_{i} ',
                        'stop': i == n_predict - 1
                    }
                    await response.write(json.dumps(chunk).encode() + b'\n')
                    
                    # Simulate token generation speed
                    await asyncio.sleep(1 / self.tokens_per_sec)
                
                await response.write_eof()
                return response
            else:
                # Non-streaming response
                content = ' '.join([f'token_{i}' for i in range(n_predict)])
                return web.json_response({
                    'content': content,
                    'tokens_generated': n_predict
                })
        
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def generate(self, request):
        """Simulated generate endpoint (Ollama style)"""
        try:
            data = await request.json()
            prompt = data.get('prompt', '')
            stream = data.get('stream', False)
            
            # Simulate TTFT
            await asyncio.sleep(self.latency_ms / 1000)
            
            if stream:
                response = web.StreamResponse()
                response.headers['Content-Type'] = 'application/json'
                await response.prepare(request)
                
                # Generate tokens
                for i in range(100):
                    chunk = {
                        'response': f'word_{i} ',
                        'done': i == 99
                    }
                    await response.write(json.dumps(chunk).encode() + b'\n')
                    await asyncio.sleep(1 / self.tokens_per_sec)
                
                await response.write_eof()
                return response
            else:
                return web.json_response({
                    'response': 'Generated response text',
                    'done': True
                })
        
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def openai_completion(self, request):
        """Simulated OpenAI-compatible endpoint (vLLM style)"""
        try:
            data = await request.json()
            prompt = data.get('prompt', '')
            max_tokens = data.get('max_tokens', 100)
            
            # Simulate TTFT + generation
            await asyncio.sleep(self.latency_ms / 1000)
            await asyncio.sleep(max_tokens / self.tokens_per_sec)
            
            return web.json_response({
                'choices': [{
                    'text': ' '.join([f'token_{i}' for i in range(max_tokens)]),
                    'finish_reason': 'stop'
                }],
                'usage': {
                    'completion_tokens': max_tokens
                }
            })
        
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def stats(self, request):
        """Stats endpoint"""
        return web.json_response({
            'requests_served': self.request_count,
            'latency_ms': self.latency_ms,
            'tokens_per_sec': self.tokens_per_sec
        })
    
    def create_app(self):
        """Create the web application"""
        app = web.Application()
        
        # Routes
        app.router.add_get('/health', self.health)
        app.router.add_post('/completion', self.completion)
        app.router.add_post('/api/generate', self.generate)
        app.router.add_post('/v1/completions', self.openai_completion)
        app.router.add_get('/stats', self.stats)
        app.router.add_get('/api/tags', self.health)  # Ollama health check
        
        return app
    
    async def run(self):
        """Run the server"""
        app = self.create_app()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        print(f"🚀 Mock Inference Server Running")
        print(f"{'=' * 60}")
        print(f"  Address: http://localhost:{self.port}")
        print(f"  Latency: {self.latency_ms}ms (simulated TTFT)")
        print(f"  Speed:   {self.tokens_per_sec} tokens/sec")
        print()
        print(f"Endpoints:")
        print(f"  GET  /health            - Health check")
        print(f"  POST /completion        - llama.cpp style")
        print(f"  POST /api/generate      - Ollama style")
        print(f"  POST /v1/completions    - OpenAI/vLLM style")
        print(f"  GET  /stats             - Server stats")
        print()
        print(f"Test with:")
        print(f"  curl http://localhost:{self.port}/health")
        print()
        print(f"Run llamabench against this server:")
        print(f"  python llamabench.py run --model llama-3.1-8b --engines llama.cpp")
        print()
        print(f"Press Ctrl+C to stop")
        print(f"{'=' * 60}")
        
        # Keep running
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            pass


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Mock inference server for testing')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    parser.add_argument('--latency', type=int, default=150, help='Simulated latency in ms')
    parser.add_argument('--speed', type=int, default=40, help='Tokens per second')
    
    args = parser.parse_args()
    
    server = MockInferenceServer(
        port=args.port,
        latency_ms=args.latency,
        tokens_per_sec=args.speed
    )
    
    try:
        await server.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Server stopped by user")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
