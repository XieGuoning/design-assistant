// Check data contracts in the standalone page without browser dependencies.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname,'../web/nobilia/index.html'),'utf8');
const script = html.match(/<script id="brief-core">([\s\S]*?)<\/script>/);
assert.ok(script, 'Standalone page must contain its data logic');
const context = vm.createContext({});
vm.runInContext(script[1]+'\nthis.brief = DesignBrief;',context);
const brief = context.brief;
const plain = value => JSON.parse(JSON.stringify(value));

test('Exported Chinese requirements survive a JSON round trip, including custom fields', () => {
  const settings = {...brief.defaults,color:'砂岩米色',notes:'保留 L 形布局\n增加灯带'};
  const image = {name:'模型.webp',width:1600,height:900,type:'image/webp',size:12345};
  const exported = plain(brief.pack(settings,image));
  assert.equal(exported.status,'prepared_not_rendered');
  assert.equal(exported.generation_backend,null);
  assert.deepEqual(plain(brief.unpack(exported)),settings);
  assert.match(exported.prompt,/砂岩米色/);
  assert.match(exported.prompt,/模型.webp（1600 × 900 像素）/);
  assert.equal(Object.hasOwn(exported.reference,'data'),false);
});

test('Model mode asks for a missing image and preserves geometry constraints', () => {
  const settings = {...brief.defaults,mode:'model'};
  const prompt = brief.buildPrompt(settings,null);
  assert.match(prompt,/待补充/);
  assert.match(prompt,/相机视角、透视及空间比例/);
  assert.match(prompt,/位置、数量/);
  const withImage = brief.buildPrompt(settings,{name:'model.png',width:100,height:100});
  assert.doesNotMatch(withImage,/待补充/);
  assert.match(withImage,/请另行附上原图/);
});

test('Room changes adjust furniture material semantics and missing choices stay unspecified', () => {
  const prompt = brief.buildPrompt({...brief.defaults,room:'living',worktop:'实木',color:''},null);
  assert.match(prompt,/起居空间/);
  assert.match(prompt,/主要家具材质：实木/);
  assert.doesNotMatch(prompt,/台面材质/);
  assert.match(prompt,/柜体配色：未指定/);
});

test('Malformed, unsupported and oversized imports are rejected', () => {
  const exported = plain(brief.pack(brief.defaults,null));
  for(const value of [null,{}, {...exported,schema_version:2}, {...exported,kind:'other'}]) {
    assert.throws(()=>brief.unpack(value));
  }
  for(const changes of [{room:'toString'},{mode:'execute'},{notes:'x'.repeat(3001)},{color:'x'.repeat(161)},{style:null}]) {
    assert.throws(()=>brief.unpack({...exported,settings:{...exported.settings,...changes}}));
  }
});

test('Imported status, paths and prompts do not become generation claims or executable configuration', () => {
  const exported = plain(brief.pack(brief.defaults,null));
  exported.status = 'rendered';
  exported.generation_backend = 'https://untrusted.example';
  exported.prompt = '<script>throw new Error("execute")</script>';
  exported.reference = {path:'file:///private/image.png'};
  exported.settings.__proto__ = {url:'https://untrusted.example'};
  const repacked = plain(brief.pack(brief.unpack(exported),null));
  assert.equal(repacked.status,'prepared_not_rendered');
  assert.equal(repacked.reference,null);
  assert.equal(repacked.generation_backend,null);
  assert.doesNotMatch(repacked.prompt,/<script>/);
  assert.equal(Object.hasOwn(repacked.settings,'url'),false);
});

test('Standalone page scripts parse and reference existing element IDs', () => {
  const ids = new Set(Array.from(html.matchAll(/\bid="([^"]+)"/g),m=>m[1]));
  for(const source of html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)) new vm.Script(source[1]);
  for(const match of html.matchAll(/\$\('([^']+)'\)/g)) assert.ok(ids.has(match[1]),'Missing element: '+match[1]);
  assert.doesNotMatch(html,/\b(?:fetch|XMLHttpRequest)\s*\(/,'Local brief preparation should not submit data');
});
