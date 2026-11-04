// node scripts/render_pdf.js  -> docs/recommendation.pdf (uses the preinstalled Playwright Chromium)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const root = path.resolve(__dirname, '..');
  const b = await chromium.launch(); const pg = await b.newPage();
  await pg.goto('file://' + root + '/docs/recommendation.html', { waitUntil: 'load' });
  await pg.pdf({ path: root + '/docs/recommendation.pdf', format: 'Letter', printBackground: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#666">Independent analysis of public filings - not a Florida PSC document - page <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
    margin: { top: '0.7in', bottom: '0.7in', left: '0.7in', right: '0.7in' } });
  await b.close();
})();
