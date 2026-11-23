// Midterm deck (Lithuanian, 7 slides + 1 backup). Build: NODE_PATH=<dir with pptxgenjs> node build_deck.js
// Figures come from make_figs.py (run it from anomaly_detection/). Numbers come from ../experiments_anomaly.csv and the paper.
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL_DIR + "/scripts/apply_theme.js");

const THEME = {
  name: "Anomalijos",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1F2933", lt1: "FFFFFF", dk2: "374151", lt2: "F3F4F6",
    accent1: "1B998B",   // teal: normal behaviour / our results
    accent2: "E4572E",   // orange: anomalies
    accent3: "9CA3AF", accent4: "6B7280", accent5: "F2B134", accent6: "2A6F97",
    hlink: "1B998B", folHlink: "6B7280",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "ECMI 2026: anomalijų aptikimas";
pres.author = "[Komandos pavadinimas]";
const C = pres.SchemeColor;
const LEFT = 0.6, WIDTH = 12.13;

pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: C.text1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: LEFT, y: 1.15, w: WIDTH, h: 1.1, fontSize: 44, bold: true, color: C.background1, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: LEFT, y: 0.35, w: WIDTH, h: 0.85, fontSize: 32, bold: true, color: C.text1, align: "left", valign: "middle", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.6, h: 0.3, fontSize: 12, color: C.accent4, align: "right" },
});

const txt = (slide, text, o) => slide.addText(text, { isTextBox: true, margin: 0, valign: "top", color: C.text1, fontSize: 14, ...o });
const card = (slide, x, y, w, h, fill, name) =>
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: fill, width: 0 }, objectName: name });

// ---------------------------------------------------------------- 1. title + problem
{
  const s = pres.addSlide({ masterName: "TITLE_DARK" });
  txt(s, "ECMI 2026 studentų konkursas · tarpinė ataskaita", { x: LEFT, y: 0.55, w: WIDTH, h: 0.4, fontSize: 16, color: C.accent3, objectName: "Kicker" });
  s.addText("Jutiklių duomenų anomalijų aptikimas", { placeholder: "title" });
  txt(s, "Dėžė važiuojančiame automobilyje: GNSS ir IMU duomenys iš Novi Sado", { x: LEFT, y: 2.2, w: WIDTH, h: 0.5, fontSize: 22, color: C.background2, objectName: "Subtitle" });

  card(s, LEFT, 3.35, 5.55, 2.0, C.text2, "Card konkursas");
  txt(s, "Konkurso formuluotė", { x: LEFT + 0.35, y: 3.55, w: 4.9, h: 0.4, fontSize: 16, bold: true, color: C.accent5, objectName: "Card konkursas antraštė" });
  txt(s, "Genda jutiklis: akselerometro ir magnetometro rodmenys neatitinka transporto priemonės judėjimo", { x: LEFT + 0.35, y: 4.0, w: 4.9, h: 1.2, fontSize: 18, color: C.background1, objectName: "Card konkursas tekstas" });
  s.addText("=", { x: 6.3, y: 3.75, w: 0.7, h: 1.2, fontFace: "Cambria", fontSize: 48, bold: true, color: C.accent2, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "Lygybė" });
  card(s, 7.18, 3.35, 5.55, 2.0, C.text2, "Card duomenys");
  txt(s, "Duomenyse (Savic ir kt., 2021)", { x: 7.53, y: 3.55, w: 4.9, h: 0.4, fontSize: 16, bold: true, color: C.accent5, objectName: "Card duomenys antraštė" });
  txt(s, "Dėžė tyčia purtoma ir verčiama: šie įvykiai pažymėti kaip anomalijos", { x: 7.53, y: 4.0, w: 4.9, h: 1.2, fontSize: 18, color: C.background1, objectName: "Card duomenys tekstas" });

  txt(s, "Abiem atvejais IMU rodo tai, ko važiavimas nepaaiškina. Tikslas: be etikečių rasti tuos momentus.", { x: LEFT, y: 5.65, w: WIDTH, h: 0.5, fontSize: 20, color: C.background1, objectName: "Tikslas" });
  txt(s, "[Komandos pavadinimas] · [Vardai ir pavardės] · [Data]", { x: LEFT, y: 6.75, w: WIDTH, h: 0.35, fontSize: 14, color: C.accent3, objectName: "Komanda" });
  s.addNotes(
    "Sveiki. Mūsų projektas yra ECMI 2026 studentų konkurso užduotis. Automobilyje važiuoja dėžė su jutiklių mazgu: jis turi GPS ir inercinį jutiklį, kuris matuoja pagreitį ir magnetinį lauką. Reikia rasti momentus, kai šie rodmenys neatitinka įprasto judėjimo. Konkurso aprašyme sakoma, kad genda jutiklis. Tačiau duomenų autorių straipsnyje paaiškinta, kad testo anomalijos yra tyčia sukeltas dėžės purtymas ir vertimas. Mums tai atrodo vienodai: inercinis jutiklis rodo tai, ko važiavimas nepaaiškina. Svarbiausia, kad mokymo duomenys neturi etikečių, todėl modelis turi išmokti tik normalų elgesį. Šiandien trumpai parodysime, kokie yra duomenys, ką jau yra padarę straipsnio autoriai, ką pamatėme duomenyse ir ką pasiekia paprastas GRU modelis, kurį paėmėme kaip pradinį tašką."
  );
}

// ---------------------------------------------------------------- 2. first look at the data
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("Pirmas žvilgsnis: |a| beveik pastovus, |B| ne", { placeholder: "title" });
  s.addImage({ path: "fig_overview.png", x: LEFT, y: 1.4, w: WIDTH, h: 3.6, altText: "Pagreičio ir magnetinio lauko ilgio pasiskirstymas ir gravitacijos ašis, mokymo ir testo duomenys", objectName: "Pirmo žvilgsnio vaizdas" });
  const cards = [
    ["98 % / 95 %", "mokymo / testo eilučių su |a| tarp 9,5 ir 10,5 m/s², arti g", C.accent1],
    ["32–116 µT", "90 % mokymo eilučių |B| (visas diapazonas 15–172 µT)", C.accent2],
    ["90 % / 82 %", "eilučių, kuriose gravitacija krenta į z ašį (mokymo / testo)", C.accent1],
  ];
  const cw = 3.91, gap = 0.2;
  cards.forEach(([big, small, col], i) => {
    const x = LEFT + i * (cw + gap);
    card(s, x, 5.2, cw, 1.6, C.background2, `Kortelė ${i + 1}`);
    txt(s, big, { x: x + 0.3, y: 5.32, w: cw - 0.6, h: 0.6, fontFace: "Cambria", fontSize: 30, bold: true, color: col, objectName: `Kortelė ${i + 1} skaičius` });
    txt(s, small, { x: x + 0.3, y: 5.97, w: cw - 0.6, h: 0.75, fontSize: 14, objectName: `Kortelė ${i + 1} tekstas` });
  });
  s.addNotes(
    "Prieš modeliuodami, pažiūrėjome į duomenis paprastai. Kairėje pagreičio vektoriaus ilgis: beveik visada apie 9,8 m/s², tai sunkio pagreitis, nes dėžė didžiąją laiko dalį ramiai guli. Tai rodo, kad akselerometras veikia ir kad pagreičio ilgis nepriklauso nuo dėžės padėties. Pastebėkime, kad mokymo ir testo pikai skiriasi maždaug 0,2 m/s², tad rodmenų poslinkis tarp įrašų šiek tiek skiriasi. Viduryje magnetinio lauko ilgis, kuris priešingai labai svyruoja, nuo maždaug 15 iki 170 mikroteslų, greičiausiai dėl metalo ir magnetų aplinkoje. Dešinėje matyti, kad apie 90 procentų mokymo eilučių sunkis patenka į z ašį, o teste tik 82 procentai, taigi testo duomenyse dėžė dažniau pasukta kitaip."
  );
}

// ---------------------------------------------------------------- 3. data
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("Duomenys: 14 stulpelių, naudojame 6", { placeholder: "title" });

  // pipeline: raw samples -> RMS -> one row
  const steps = [["IMU mėginiai", "kas ~15 ms (~67 Hz)"], ["RMS per intervalą", "~10 s (kovo laikas apvalintas)"], ["Viena lentelės eilutė", "kartu su GPS reikšmėmis"]];
  const bw = 2.55, bx = [LEFT, LEFT + 2.95, LEFT + 5.9];
  steps.forEach(([a, b], i) => {
    card(s, bx[i], 1.45, bw, 1.0, C.background2, `Žingsnis ${i + 1}`);
    txt(s, a, { x: bx[i] + 0.2, y: 1.55, w: bw - 0.4, h: 0.4, fontSize: 16, bold: true, objectName: `Žingsnis ${i + 1} pavadinimas` });
    txt(s, b, { x: bx[i] + 0.2, y: 1.97, w: bw - 0.4, h: 0.4, fontSize: 14, color: C.accent4, objectName: `Žingsnis ${i + 1} paaiškinimas` });
    if (i < 2) s.addText("→", { x: bx[i] + bw, y: 1.6, w: 0.4, h: 0.7, fontSize: 28, bold: true, color: C.accent2, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `Rodyklė ${i + 1}` });
  });

  const rows = [
    ["IMU: 6 stulpeliai", "ACC x, y, z · MAG x, y, z", "NAUDOJAME. Pagreitis rodo purtymą ir dėžės padėtį (sunkis ~9,8 m/s² krenta į vieną ašį), magnetinis laukas keičiasi ją verčiant.", C.accent1],
    ["GPS: 5 stulpeliai", "lat, lon, alt, speed, num_sats", "Nenaudojame. Testo duomenyse vietos anomalijų nėra, kovą greitis visada 0 (vienetas nenurodytas, tikėtina mazgai), 7–12 % eilučių be GPS fiksacijos.", C.accent4],
    ["Apskaita: 3 stulpeliai", "timestamp, ACC_samples, MAG_samples", "Nenaudojame. Laikas ir mėginių skaičius intervale (~546), tai ne fizinis signalas.", C.accent4],
  ];
  rows.forEach(([a, b, c, col], i) => {
    const y = 2.8 + i * 1.35;
    card(s, LEFT, y, 2.9, 1.2, col, `Grupė ${i + 1}`);
    txt(s, a, { x: LEFT + 0.2, y: y + 0.17, w: 2.5, h: 0.4, fontSize: 18, bold: true, color: C.background1, objectName: `Grupė ${i + 1} pavadinimas` });
    txt(s, b, { x: LEFT + 0.2, y: y + 0.65, w: 2.55, h: 0.45, fontSize: 14, color: C.background1, objectName: `Grupė ${i + 1} stulpeliai` });
    txt(s, c, { x: LEFT + 3.15, y: y + 0.05, w: 5.75, h: 1.1, fontSize: 14, valign: "middle", objectName: `Grupė ${i + 1} aprašas` });
  });

  // right panel: sizes
  card(s, 9.75, 1.45, 2.98, 5.15, C.text1, "Skaičių skydelis");
  const facts = [["12 678", "mokymo eilutės"], ["1 571", "testo eilutės"], ["39", "pažymėtos anomalijos"], ["~12 %", "eilučių be GPS fiksacijos teste"]];
  facts.forEach(([big, small], i) => {
    const y = 1.7 + i * 1.22;
    txt(s, big, { x: 10.0, y, w: 2.5, h: 0.6, fontFace: "Cambria", fontSize: 32, bold: true, color: C.accent5, objectName: `Skaičius ${i + 1}` });
    txt(s, small, { x: 10.0, y: y + 0.6, w: 2.5, h: 0.5, fontSize: 14, color: C.background1, objectName: `Skaičiaus ${i + 1} paaiškinimas` });
  });
  s.addNotes(
    "Duomenis surinko Novi Sado universiteto komanda. Jutiklis matuoja pagreitį maždaug kas penkiolika milisekundžių, o GPS kas dešimt sekundžių. Kiekvienai GPS eilutei įrenginys suskaičiuoja pagreičio ir magnetinio lauko vidutinį kvadratinį nuokrypį, RMS, todėl lentelėje yra keturiolika stulpelių. Pagrindiniam modeliui paėmėme tik šešis inercinio jutiklio stulpelius. Straipsnis sako, kad anomalijos yra dėžės purtymas ir vertimas, o jį matuoja būtent pagreitis ir magnetinis laukas. GPS nenaudojame, nes vietos anomalijų nėra, o kovo mėnesį greitis visada nulis. Mėginių skaičiaus stulpeliai yra tik apskaita. Dar viena smulkmena: faile nenurodyta, kokiais vienetais matuojamas greitis. Palyginę su koordinačių pokyčiu, spėjame, kad tai mazgai, bet tai tik išvada. Prieš mokymą kiekvieną stulpelį standartizuojame pagal mokymo duomenų vidurkį ir nuokrypį."
  );
}

// ---------------------------------------------------------------- 4. literature
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("Savic ir kt. (2021): autoenkoderiai", { placeholder: "title" });
  txt(s, "Ką padarė", { x: LEFT, y: 1.45, w: 5.6, h: 0.4, fontSize: 20, bold: true, color: C.accent1, objectName: "Ką padarė" });
  s.addText([
    { text: "Autoenkoderis mokosi tik normalių duomenų, anomalija = didelė atkūrimo klaida", options: { bullet: true, breakLine: true } },
    { text: "„Edge“ modelis (jutiklyje) mato vieną eilutę, „fog“ modelis (serveryje) paskutines L eilučių", options: { bullet: true, breakLine: true } },
    { text: "Palyginta su 5 PyOD metodais; vertinta įvykių tikslumu, pilnumu ir F1", options: { bullet: true } },
  ], { x: LEFT, y: 1.9, w: 5.6, h: 2.2, fontSize: 16, color: C.text1, valign: "top", margin: 0, paraSpaceAfter: 8, isTextBox: true, objectName: "Ką padarė sąrašas" });
  txt(s, "Kas lieka neaišku", { x: LEFT, y: 4.15, w: 5.6, h: 0.4, fontSize: 20, bold: true, color: C.accent2, objectName: "Neaišku" });
  s.addText([
    { text: "Tekste slenkstis yra didžiausia mokymo klaida, kode 95 procentilė", options: { bullet: true, breakLine: true } },
    { text: "Tekste 42 anomalijos, rezultatų lentelė atitinka 39", options: { bullet: true, breakLine: true } },
    { text: "Neišbandyta: rekurentiniai tinklai ir fizikiniai požymiai", options: { bullet: true } },
  ], { x: LEFT, y: 4.6, w: 5.6, h: 2.1, fontSize: 16, color: C.text1, valign: "top", margin: 0, paraSpaceAfter: 8, isTextBox: true, objectName: "Neaišku sąrašas" });

  const labels = ["ADM-FOG autoenkoderis (L = 17)", "ADM-EDGE autoenkoderis", "ABOD", "PCA", "KNN", "HBOS", "OCSVM"];
  const values = [0.82, 0.70, 0.655, 0.597, 0.581, 0.523, 0.259];
  s.addChart(pres.charts.BAR, [{ name: "F1", labels, values }], {
    x: 6.6, y: 1.4, w: 6.13, h: 5.3, barDir: "bar", barGapWidthPct: 45,
    chartColors: ["1B998B", "1B998B", "9CA3AF", "9CA3AF", "9CA3AF", "9CA3AF", "9CA3AF"],
    showValue: true, dataLabelFormatCode: "0.00", dataLabelFontSize: 14, dataLabelColor: "1F2933", dataLabelFontFace: "+mn-lt", dataLabelPosition: "outEnd",
    catAxisOrientation: "maxMin", catAxisLabelFontSize: 14, catAxisLabelColor: "1F2933", catAxisLabelFontFace: "+mn-lt",
    valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 1, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showLegend: false, showTitle: true, title: "F1 testo duomenyse (be GPS stulpelių)", titleFontSize: 16, titleColor: "1F2933", titleFontFace: "+mn-lt",
    objectName: "Straipsnio F1 diagrama",
  });
  s.addNotes(
    "Duomenų autoriai siūlo aptikti anomalijas autoenkoderiu. Tai neuroninis tinklas, kuris mokosi atkurti normalius duomenis. Kai atkūrimo klaida didelė, taškas laikomas anomalija. Jie turi du modelius: mažą jutiklyje, kuris mato vieną eilutę, ir didesnį serveryje, kuris mato kelias eilutes iš eilės. Diagramoje matote straipsnio rezultatus: serverio modelis pasiekia maždaug 0,82, jutiklio modelis apie 0,70, o geriausias klasikinis metodas ABOD 0,66. Dar radome dvi smulkmenas. Tekste slenkstis yra didžiausia mokymo klaida, bet kode naudojama 95 procentilė, o rezultatus atkartojame tik su kodo variantu. Be to, tekste yra 42 anomalijos, o lentelės atitinka 39. Rekurentinių tinklų ir fizikinių požymių autoriai neišbandė. Tai nereiškia, kad straipsnyje klaida: aprašymas ir kodas tiesiog skiriasi, todėl lyginamės su kodo variantu."
  );
}

// ---------------------------------------------------------------- 5. data analysis
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("Anomalijos: dėžė apverčiama ir purtoma", { placeholder: "title" });
  s.addImage({ path: "fig_anomaly.png", x: LEFT, y: 1.4, w: 6.3, h: 4.2, altText: "Pagreitis ir magnetinis laukas aplink pažymėtas anomalijas: gravitacija peršoka tarp ašių", objectName: "Anomalijų vaizdas" });
  txt(s, "Raudonos linijos: pažymėtos anomalijos. Gravitacija (~9,8 m/s²) peršoka iš vienos ašies į kitą, magnetinio lauko komponentės šoktelia kartu.", { x: LEFT, y: 5.7, w: 6.3, h: 0.7, fontSize: 14, color: C.accent4, objectName: "Anomalijų paaiškinimas" });
  s.addImage({ path: "fig_sessions.png", x: 7.2, y: 1.4, w: 5.5, h: 3.0, altText: "Magnetinio lauko dydis kiekvienoje sesijoje", objectName: "Sesijų vaizdas" });
  txt(s, "Magnetinio lauko lygis priklauso nuo sesijos, todėl vienas bendras slenkstis netinka.", { x: 7.2, y: 4.5, w: 5.5, h: 0.7, fontSize: 14, color: C.accent4, objectName: "Sesijų paaiškinimas" });

  card(s, 7.2, 5.3, 2.7, 1.45, C.background2, "Skaičius 1 kortelė");
  txt(s, "26 iš 39", { x: 7.4, y: 5.4, w: 2.4, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: C.accent2, objectName: "Skaičius 1" });
  txt(s, "anomalijų ±1 min. nuo gravitacijos ašies šuolio", { x: 7.4, y: 6.0, w: 2.4, h: 0.7, fontSize: 14, objectName: "Skaičius 1 paaiškinimas" });
  card(s, 10.03, 5.3, 2.7, 1.45, C.background2, "Skaičius 2 kortelė");
  txt(s, "22 vs 6 µT", { x: 10.23, y: 5.4, w: 2.4, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: C.accent1, objectName: "Skaičius 2" });
  txt(s, "|B| skirtumas tarp sesijų ir sesijos viduje", { x: 10.23, y: 6.0, w: 2.4, h: 0.7, fontSize: 14, objectName: "Skaičius 2 paaiškinimas" });
  s.addNotes(
    "Kairėje matote dvidešimties minučių ištrauką iš testo duomenų. Viršuje pagreitis trimis ašimis, apačioje magnetinis laukas, o raudonos linijos yra pažymėtos anomalijos. Dėžei gulint ramiai, sunkio jėga, maždaug 9,8, patenka į vieną ašį. Kai dėžė apverčiama, ši reikšmė peršoka į kitą ašį, o magnetinio lauko komponentės šoktelia kartu. Dvidešimt šešiose iš trisdešimt devynių anomalijų tokį šuolį randame per minutę nuo žymos. Dešinėje matote kitą svarbų dalyką. Magnetinio lauko stiprumas tarp sesijų skiriasi apie dvidešimt du mikroteslas, o sesijos viduje tik apie šešis. Todėl svarbus ne lygis, o pokytis. Dar pastaba: apie trisdešimt procentų testo eilučių yra per minutę nuo kokios nors anomalijos, nes kovo mėnesį laikas suapvalintas iki minutės, tad žymos yra gana grubios."
  );
}

// ---------------------------------------------------------------- 6. GRU baseline
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("Paprastas GRU autoenkoderis: F1 ≈ 0,82", { placeholder: "title" });
  const boxes = [["Langas", "10 eilučių × 6 IMU stulpeliai"], ["GRU koduotojas", "perskaito langą"], ["8 skaičiai", "suspaustas langas"], ["GRU dekoderis", "atkuria langą"], ["Atkūrimo klaida", "didelė = anomalija"]];
  const bw2 = 2.15, step = 2.495;
  boxes.forEach(([a, b], i) => {
    const x = LEFT + i * step, fill = i === 2 ? C.accent1 : C.background2, fg = i === 2 ? C.background1 : C.text1;
    card(s, x, 1.4, bw2, 1.05, fill, `Schema ${i + 1}`);
    txt(s, a, { x: x + 0.15, y: 1.5, w: bw2 - 0.3, h: 0.4, fontSize: 16, bold: true, color: fg, objectName: `Schema ${i + 1} pavadinimas` });
    txt(s, b, { x: x + 0.15, y: 1.92, w: bw2 - 0.3, h: 0.45, fontSize: 14, color: fg, objectName: `Schema ${i + 1} paaiškinimas` });
    if (i < 4) s.addText("→", { x: x + bw2, y: 1.55, w: 0.345, h: 0.75, fontSize: 24, bold: true, color: C.accent2, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `Schemos rodyklė ${i + 1}` });
  });
  txt(s, "Slenkstis = 95 % mokymo klaidų (be testo etikečių). Vertinimas pagal straipsnio įvykių metriką.", { x: LEFT, y: 2.6, w: WIDTH, h: 0.35, fontSize: 14, color: C.accent4, objectName: "Slenkstis" });

  const labels = ["Straipsnis: tankusis AE, 1 eilutė", "Mūsų atkartojimas, 1 eilutė", "GRU AE, langas 5", "GRU AE, langas 10", "LSTM AE, langas 10", "GRU AE, langas 20"];
  const values = [0.693, 0.70, 0.745, 0.818, 0.818, 0.816];
  s.addChart(pres.charts.BAR, [{ name: "F1", labels, values }], {
    x: LEFT, y: 3.05, w: 7.7, h: 3.8, barDir: "bar", barGapWidthPct: 40,
    chartColors: ["9CA3AF", "9CA3AF", "1B998B", "1B998B", "1B998B", "1B998B"],
    showValue: true, dataLabelFormatCode: "0.00", dataLabelFontSize: 14, dataLabelColor: "1F2933", dataLabelFontFace: "+mn-lt", dataLabelPosition: "outEnd",
    catAxisOrientation: "maxMin", catAxisLabelFontSize: 14, catAxisLabelColor: "1F2933", catAxisLabelFontFace: "+mn-lt",
    valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 1, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showLegend: false, showTitle: false, objectName: "Mūsų F1 diagrama",
  });
  card(s, 8.6, 3.15, 4.13, 3.6, C.text1, "Rezultato skydelis");
  txt(s, "0,82", { x: 8.9, y: 3.3, w: 3.5, h: 1.0, fontFace: "Cambria", fontSize: 60, bold: true, color: C.accent5, objectName: "Rezultatas F1" });
  txt(s, "F1: GRU, langas 10", { x: 8.9, y: 4.3, w: 3.5, h: 0.4, fontSize: 16, color: C.background1, objectName: "Rezultato pavadinimas" });
  txt(s, "tikslumas 0,74 · pilnumas 0,92\n36 iš 39 anomalijų, 13 klaidingų aliarmų", { x: 8.9, y: 4.7, w: 3.5, h: 0.85, fontSize: 16, color: C.background1, objectName: "Rezultato detalės" });
  txt(s, "Atskaita: atsitiktinis detektorius su tiek pat pažymėtų langų (48 %) gauna 0,30; „visada anomalija“ gauna 0,95, nes šioje metrikoje iš eilės einantys klaidingi aliarmai skaičiuojami kaip vienas.", { x: 8.9, y: 5.6, w: 3.5, h: 1.05, fontSize: 12, color: C.background2, objectName: "Atskaitos taškai" });
  s.addNotes(
    "Kaip paprastą bazinį modelį paėmėme GRU autoenkoderį. Į jį paduodame dešimties eilučių langą su šešiais inercinio jutiklio stulpeliais, tinklas suspaudžia jį į aštuonis skaičius ir bando atkurti. Slenkstį nustatome iš mokymo duomenų, ne iš testo etikečių. Pirmiausia patikrinome savo kodą: straipsnio tankųjį autoenkoderį atkartojome ir gavome 0,70, kai straipsnyje 0,693. Vienos eilutės modelis lieka apie 0,70, o laiko langas pakelia rezultatą iki 0,82. Tikslumas 0,74, pilnumas 0,92: rasta trisdešimt šešios iš trisdešimt devynių anomalijų. LSTM duoda tą patį. Rezultatas panašus į geriausią straipsnio modelį, nors modelis paprastas ir be fizikos. Svarbi pastaba apie metriką: ji dosni, nes iš eilės einantys klaidingi aliarmai skaičiuojami kaip vienas. Detektorius, kuris visada sako anomalija, gautų 0,95, o atsitiktinis su tiek pat pažymėtų langų tik 0,30. Todėl F1 naudojame palyginimui su straipsniu, o papildomai skaičiuojame nuo slenksčio nepriklausomą AUROC, kuris mūsų GRU modeliui yra 0,85. Dvi pastabos dėl sąžiningumo. Slenkstį pasirinkome iš anksto pagal straipsnio kodą, 95 procentilę, o su 99 procentile rezultatas beveik toks pat, 0,83. Paėmus straipsnio vienuolika stulpelių rezultatas šiek tiek prastesnis, 0,79. Be to, modelis iš dalies gali tiesiog atpažinti labiau judinamas sesijas, todėl toliau žiūrėsime rezultatus pagal sesijas."
  );
}

// ---------------------------------------------------------------- 7. next steps
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("Toliau: fizika ir patikimas vertinimas", { placeholder: "title" });
  txt(s, "Klausimas: ar fizikiniai požymiai pranoksta žaliavinius IMU stulpelius?", { x: LEFT, y: 1.3, w: WIDTH, h: 0.4, fontSize: 18, color: C.accent4, objectName: "Klausimas" });
  const steps = [
    ["1", "Fizikiniai požymiai", "gravitacijos ašis ir jos šuoliai, |a| − g, magnetinio lauko pokytis sesijos viduje"],
    ["2", "Modelių palyginimas", "taisyklės, GMM, tankusis AE, GRU AE: ką duoda kiekvienas"],
    ["3", "Patikimas vertinimas", "slenkstis be testo etikečių, AUROC, rezultatai pagal sesijas"],
    ["4", "Duomenų tvarkymas", "pašalinus ~77 apvertimus iš mokymo, AUROC beveik nepakito; ieškosime kitų nešvarumų"],
  ];
  const cw = 2.85, gap = 0.243;
  steps.forEach(([n, a, b], i) => {
    const x = LEFT + i * (cw + gap);
    card(s, x, 2.0, cw, 3.7, C.background2, `Žingsnis ${n} kortelė`);
    s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: 2.3, w: 0.8, h: 0.8, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 }, objectName: `Žingsnis ${n} apskritimas` });
    s.addText(n, { x: x + 0.3, y: 2.3, w: 0.8, h: 0.8, fontFace: "Cambria", fontSize: 28, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `Žingsnis ${n} numeris` });
    txt(s, a, { x: x + 0.3, y: 3.3, w: cw - 0.6, h: 0.7, fontSize: 20, bold: true, objectName: `Žingsnis ${n} pavadinimas` });
    txt(s, b, { x: x + 0.3, y: 4.05, w: cw - 0.6, h: 1.5, fontSize: 16, objectName: `Žingsnis ${n} aprašas` });
  });
  txt(s, "Ataskaita (≤ 12 psl.) ir kodas: 2027-02-28", { x: LEFT, y: 6.1, w: WIDTH, h: 0.5, fontSize: 20, bold: true, color: C.accent2, objectName: "Terminas" });
  s.addNotes(
    "Toliau norime atsakyti į vieną klausimą: ar fizikiniai požymiai geresni už žaliavinius stulpelius. Pirma, suskaičiuosime požymius, kurie atsiranda iš fizikos: gravitacijos ašį ir jos šuolius, pagreičio dydį atėmus sunkį ir magnetinio lauko pokytį sesijos viduje. Antra, palyginsime kelis modelius: paprastas taisykles, Gauso mišinį, tankųjį autoenkoderį ir GRU. Trečia, slenkstį rinksimės be testo etikečių ir rezultatus žiūrėsime pagal sesijas ir pagal nuo slenksčio nepriklausomą AUROC, kad pamatytume, ar modelis tikrai aptinka įvykius, o ne tik nerimastingas sesijas. Ketvirta, patikrinome mokymo duomenis, kuriuose yra apie septyniasdešimt septyni apvertimai: juos pašalinus rezultatas beveik nepasikeitė, todėl tai mažesnė problema, nei tikėjomės. Ataskaitą ir kodą pateiksime iki 2027 metų vasario 28 dienos. Tikimės, kad fizikiniai požymiai ne tik pagerins rezultatą, bet ir paaiškins, kodėl modelis klysta. Ačiū, laukiame klausimų."
  );
}

// ---------------------------------------------------------------- 8. backup
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("Priedas: kur atkūrimo klaida didelė", { placeholder: "title" });
  s.addImage({ path: "fig_timeline.png", x: LEFT, y: 1.4, w: 12.13, h: 3.93, altText: "Atkūrimo klaida kiekvienam testo langui; oranžiniai taškai virš slenksčio", objectName: "Klaidų laiko eilutė" });
  txt(s, "Oranžiniai taškai viršija slenkstį, raudonos linijos žymi pažymėtas anomalijas. Oranžiniai taškai be raudonos linijos šalia yra klaidingi aliarmai.", { x: LEFT, y: 5.5, w: WIDTH, h: 0.7, fontSize: 16, color: C.accent4, objectName: "Klaidų paaiškinimas" });
  s.addNotes("Atsarginė skaidrė klausimams: GRU modelio (langas 10) atkūrimo klaida kiekvienam testo langui, laiko tvarka. Daugiausia aptikimų yra sausio važiavime ir kovo 21–23 d. sesijose, kur dėžė judinama labiausiai.");
}

(async () => {
  await pres.writeFile({ fileName: "midterm.pptx" });
  await applyTheme("midterm.pptx", THEME);
  console.log("written midterm.pptx");
})();
