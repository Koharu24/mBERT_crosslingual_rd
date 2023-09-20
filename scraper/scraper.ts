import puppeteer from "puppeteer";
import { unlink } from "node:fs/promises";
import assert from "assert";

function shuffleArray<T>(arr: T[]): T[] {
  let currentIndex = arr.length, randomIndex: number;

  while (currentIndex !== 0) {
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex--;

    [arr[currentIndex], arr[randomIndex]] = [
      arr[randomIndex],
      arr[currentIndex],
    ];
  }

  return arr;
}

const validWordTypes = {
  "en": [
    "Verb",
    "Noun",
    "Adjective",
    "Adverb",
    "Interjection",
    "Pronoun",
  ],
  "it": [
    "Verb",
    "Sost",
    "Agg",
    "Avv",
    "Inter",
    "Prono",
  ],
  "de": [
    "Verb",
    "Substantiv",
    "Adjektiv",
    "Adverb",
    "Interjektion",
    "Pronomen",
  ],
  "ja": [
    "動詞",
    "名詞",
    "形容詞",
    "副詞",
    "間投詞",
    "代名詞",
  ],
};

const chunkArray = (array: string[], size: number): string[][] => {
  const chunks = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
};

const extractDefinitions = async (
  word: string,
  page: any,
  maxNumber: number = 10,
  language = "en",
): Promise<[string, string][]> => {
  word = word.replace(" ", "_");
  const url = `https://${language}.wiktionary.org/wiki/${word}`;
  console.log(`Going to ${url}`);
  const response = await page.goto(url);
  if (response.status() === 404) {
    return [];
  }
  try {
    await page.waitForSelector("ol");
  } catch (e) {
    console.log(`Error on ${word}`);
    return [];
  }
  let foundDefinitions: string[] = [];
  if (language === "de") {
    foundDefinitions = await page.evaluate(() => {
      const targetP = Array.from(document.querySelectorAll("*"))
        .filter((element) =>
          element.innerText.toLowerCase() === "bedeutungen:"
        )[0];
      let nextSibling = targetP.nextElementSibling!;
      const texts = Array.from(nextSibling.querySelectorAll("dd")).map(
        (el) => el.innerText,
      );
      const cleanedTexts = texts
        .filter((def: string) => !/\[\d+\] .+ \[\d+\]/.test(def)).map((
          def: string,
        ) => def.replace(/^\[\d+\] /, "")).map((x) => x.trim());
      return cleanedTexts;
    });
  } else {
    foundDefinitions = (await page.evaluate((validWordType: string[]) => {
      const innerFoundDefinitions = [];

      const h3Elements = Array.from(
        document.querySelectorAll("h3 span.mw-headline"),
      );
      const found = validWordType.map(
        (form) =>
          h3Elements.filter((el) =>
            (el !== undefined) &&
            el.innerText.toLowerCase().includes(form.toLowerCase())
          )[0],
      );
      found.forEach((targetH3) => {
        if (!targetH3) return [];
        console.log(targetH3.innerText);
        let nextSibling = targetH3.parentElement.nextElementSibling;
        while (nextSibling && nextSibling.tagName !== "OL") {
          nextSibling = nextSibling.nextElementSibling;
        }
        if (!nextSibling) return [];
        const listItems = Array.from(
          nextSibling.querySelectorAll(":scope > li"),
        );
        const tmpRes = listItems.map((item) =>
          item.innerText.trim().split("\n")[0]
        );
        innerFoundDefinitions.push(...tmpRes);
      });
      return innerFoundDefinitions;
    }, validWordTypes[language])).filter((el: string) => el.length > 0);
  }
  shuffleArray(foundDefinitions);
  return foundDefinitions.filter((el: string) => el.length > 1).slice(
    0,
    maxNumber,
  ).map(
    (def: string) => [
      word,
      removeStartingParenthesis(def),
    ],
  );
};

function removeStartingParenthesis(str: string) {
  return str.startsWith("(") ? str.slice(str.indexOf(")") + 1).trim() : str;
}

const createNewPage = async (browser: any, redirectConsole = true) => {
  const page = await browser.newPage();
  await page.setRequestInterception(true);

  if (redirectConsole) {
    // Intercept requests
    page.on("request", (request) => {
      const resourceType = request.resourceType();
      if (resourceType === "image" || resourceType === "script") {
        request.abort();
      } else {
        request.continue();
      }
    });
    page.on("console", (msg) => console.log("Browser console:", msg.text()));
  }
  return page;
};

const main = async (
  maxNumber: number,
  language: string,
  startFrom: number = 0,
) => {
  assert(startFrom >= 0);
  if (startFrom > 0) {
    console.log("WARNING: starfrom > 0.");
  }
  const browser = await puppeteer.launch({
    executablePath: "/usr/bin/google-chrome-unstable",
    headless: "new",
  });
  const cleanWords = (await Bun.file(`./data/${language}_filtered.txt`).text())
    .split(
      "\n",
    ).filter((word: string) => word.length > 1).map((word: string) =>
      word.trim()
    ).slice(startFrom);
  console.log(`Total words: ${cleanWords.length}`);

  const poolSize = 50;
  const pagePool = [];
  for (let i = 0; i < poolSize; i++) {
    pagePool.push(await createNewPage(browser));
  }
  const wordBatches = chunkArray(cleanWords, poolSize);

  let processedCount = 0;

  const totalCount = cleanWords.length;

  const path = `./data/${language}_definitions.jsonl`;
  const file = Bun.file(path);
  if (await file.exists()) {
    if (startFrom === 0) {
      console.log("WARNING: file already exists. Erasing it.");
      await unlink(path);
    } else {
      console.log("WARNING: file already exists. Adding data to it.");
    }
  }
  const writer = file.writer();
  for (const batch of wordBatches) {
    const promiseList = batch.map(async (word, index) => {
      const page = pagePool[index];
      const definitions = await extractDefinitions(
        word,
        page,
        maxNumber,
        language,
      );
      for (const definition of definitions) {
        await writer.write(JSON.stringify(definition) + "\n");
      }
      processedCount++;
      console.log(`Progress: ${processedCount}/${totalCount}`);
    });
    await Promise.all(promiseList);
    writer.flush();
  }

  for (const page of pagePool) {
    await page.close();
  }

  await browser.close();
};

await main(
  10,
  "ja",
  160000,
);
