"""Register a local rendered-page extractor through Hermes's native plugin API."""
import asyncio
import json
import uuid
from agent.web_search_provider import WebSearchProvider


class RailwayLocalExtract(WebSearchProvider):
    name = 'railway-local'
    display_name = 'Railway Local (Chromium)'

    def is_available(self):
        return True

    def supports_search(self):
        return False

    def supports_extract(self):
        return True

    def get_setup_schema(self):
        return {'name': self.display_name, 'badge': 'local · no extra API key',
                'tag': 'Rendered page text using the local Chromium browser.', 'env_vars': []}

    async def extract(self, urls, **kwargs):
        # Native web_extract validates input/SSRF before dispatch and performs
        # its own truncation, secret redaction and content-cache handling after.
        return await asyncio.to_thread(self._extract, urls)

    def _extract(self, urls):
        from tools.browser_tool import browser_navigate, browser_console
        from tools.browser_tool_lifecycle import _cleanup_single_browser_session
        from tools.interrupt import is_interrupted
        task = 'railway-extract-' + uuid.uuid4().hex
        results = []
        expression = ("JSON.stringify({title:document.title,url:location.href,"
                      "text:(document.querySelector('main')||document.body).innerText.slice(0,200000)})")
        try:
            for url in urls:
                try:
                    if is_interrupted():
                        results.append({'url': url, 'error': 'Interrupted', 'title': ''})
                        continue
                    nav = json.loads(browser_navigate(url, task_id=task))
                    if not nav.get('success'):
                        raise RuntimeError(nav.get('error') or 'Browser navigation failed')
                    evaluated = json.loads(browser_console(expression=expression, task_id=task))
                    if not evaluated.get('success'):
                        raise RuntimeError(evaluated.get('error') or 'Page extraction failed')
                    page = evaluated.get('result')
                    if isinstance(page, str):
                        page = json.loads(page)
                    text = (page or {}).get('text', '').strip()
                    if not text:
                        raise RuntimeError('The page has no readable text')
                    results.append({'url': url, 'title': page.get('title', ''),
                                    'content': text, 'raw_content': text,
                                    'metadata': {'sourceURL': page.get('url', url),
                                                 'extractor': 'railway-local-chromium'}})
                except Exception as exc:
                    results.append({'url': url, 'title': '', 'error': str(exc)})
        finally:
            _cleanup_single_browser_session(task)
        return results


def register(ctx):
    ctx.register_web_search_provider(RailwayLocalExtract())
