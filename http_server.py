from aiohttp import web
import json
import os

class HttpServer:
    def __init__(self, db, port=10080):
        self.db = db
        self.port = port
        self.app = web.Application()
        self.app.router.add_get('/', self.handle_index)
        self.app.router.add_get('/api/search', self.handle_search)
        self.runner = None
        self.site = None

    async def handle_index(self, request):
        # Serve the index.html file
        ui_path = os.path.join(os.path.dirname(__file__), 'ui', 'index.html')
        if os.path.exists(ui_path):
            return web.FileResponse(ui_path)
        return web.Response(text="UI not found", status=404)

    async def handle_search(self, request):
        query = request.query.get('q', '')
        camera_id = request.query.get('camera_id', None)
        
        if not query:
            return web.json_response([])

        results = self.db.search(query, camera_id)
        # Convert results to list of dicts
        json_results = []
        for row in results:
            json_results.append({
                'id': row[0],
                'camera_id': row[1],
                'timestamp': row[2],
                'text': row[3]
            })
        
        return web.json_response(json_results)

    async def start(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, '0.0.0.0', self.port)
        await self.site.start()
        print(f"HTTP Server started on port {self.port}")

    async def stop(self):
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()

