const fs = require('fs');

const inPath = 'workflow_novo.json';
const outPath = 'workflow_novo_adaptado.json';
const wf = JSON.parse(fs.readFileSync(inPath, 'utf8'));

wf.active = false;
wf.name = `${wf.name} (Adaptado)`;
if (!wf.id) {
  wf.id = `wf_${Date.now()}`;
}
delete wf.versionId;
delete wf.meta;

for (const node of wf.nodes || []) {
  switch (node.name) {
    case 'Buscar Clientes no Agendor':
      node.parameters.queryParameters.parameters[0].value = '={{ $env.AGENDOR_USER_ID }}';
      node.parameters.headerParameters.parameters[0].value = '={{ "Token " + $env.AGENDOR_API_TOKEN }}';
      node.continueOnFail = true;
      break;

    case 'Filtrar Leticia':
      node.parameters.jsCode = `const OWNER_ID = Number($env.AGENDOR_USER_ID || 0);
const MAX_CONTACTS = Number($env.CAMPAIGN_MAX_CONTACTS || 200);

const all = $input.all();
const contacts = [];

for (const item of all) {
  const data = item.json.data || [];
  for (const c of data) {
    const ownerId = Number(c?.ownerUser?.id || 0);
    const ownerMatches = OWNER_ID ? ownerId === OWNER_ID : true;
    if (ownerMatches && contacts.length < MAX_CONTACTS) {
      contacts.push(c);
    }
  }
}

console.log('Contatos filtrados: ' + contacts.length);
return [{ json: { contacts } }];`;
      break;

    case 'Formatar Dados':
      node.parameters.jsCode = `const campanha = $('Preparar Campanha').first().json;
const promoText = campanha.promoText;
const base64Image = campanha.base64Image;
const mimeType = campanha.mimeType;
const fileName = campanha.fileName;
const hasImage = campanha.hasImage;
const campaignId = campanha.campaignId;

const clients = $input.first().json.contacts || [];
const greetings = ['Oi', 'Ola', 'Oii', 'Oi, tudo bem?', 'Ola, tudo bom?'];
const result = [];
const seenPhones = new Set();
let noPhone = 0;

for (const client of clients) {
  const fullName = client.name || '';
  const firstName = fullName.split(' ')[0] || 'Cliente';

  let phone = (client.contact && (client.contact.whatsapp || client.contact.mobile || client.contact.work)) || '';
  phone = String(phone).replace(/\\D/g, '');
  if (phone.length === 10 || phone.length === 11) phone = '55' + phone;
  if (!phone || phone.length < 12) { noPhone++; continue; }
  if (seenPhones.has(phone)) continue;
  seenPhones.add(phone);

  const saudacao = greetings[Math.floor(Math.random() * greetings.length)];
  const message = String(promoText || '')
    .replace(/\\{\\{saudacao\\}\\}/gi, saudacao)
    .replace(/\\{\\{nome\\}\\}/gi, firstName)
    .replace(/\\{\\{nomeCompleto\\}\\}/gi, fullName);

  result.push({ json: { name: fullName, phone, message, hasImage, base64Image, mimeType, fileName, campaignId } });
}

console.log(
  'Contatos recebidos: ' + clients.length +
  ' | Sem tel: ' + noPhone +
  ' | A enviar: ' + result.length
);

if (result.length === 0) {
  return [{ json: { _campaignDone: true, campaignId, message: 'Nenhum contato encontrado.' } }];
}

return result;`;
      break;

    case 'Simular Digitando':
      node.parameters.instanceName = '={{ $env.EVOLUTION_INSTANCE }}';
      delete node.credentials;
      break;

    case 'Enviar com Imagem':
      node.parameters.instanceName = '={{ $env.EVOLUTION_INSTANCE }}';
      delete node.credentials;
      break;

    case 'Enviar Texto':
      node.parameters.instanceName = '={{ $env.EVOLUTION_INSTANCE }}';
      delete node.credentials;
      break;

    case 'Aguardar 40s':
      node.parameters.amount = '={{ Number($env.CAMPAIGN_DELAY_SECONDS || 40) }}';
      break;

    default:
      break;
  }
}

fs.writeFileSync(outPath, JSON.stringify(wf, null, 2), 'utf8');
console.log('Arquivo gerado:', outPath);
