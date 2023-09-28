import puppeteer from "puppeteer";
import { unlink } from "node:fs/promises";
import assert from "assert";
import chalk from "chalk";
import { exec } from "child_process";

async function lemmatizeWord(word: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const command = `python lemmatize.py ${word}`;
    exec(command, (error, stdout, stderr) => {
      if (error) {
        reject(`Error executing command: ${error}`);
        return;
      }
      resolve(stdout.trim());
    });
  });
}

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
  const url = language === "de"
    ? `https://www.dwds.de/wb/${word}`
    : `https://${language}.wiktionary.org/wiki/${word}`;
  console.log(`Going to ${url}`);
  let response = null;
  try {
    response = await page.goto(url, {
      waitUntil: "networkidle0",
    });
    console.log(`Response: ${response!.status()}`);
  } catch (e) {
    console.log(`Error: ${e}`);
    return [];
  }
  // if (response == null || response.status() === 404) {
  //   console.log(`Error: ${response.status()}`);
  //   return [];
  // }
  try {
    if (language === "de") {
      await page.waitForSelector(".dwdswb-definitionen");
    } else {
      await page.waitForFunction(() => {
        const elements = Array.from(document.querySelectorAll("*"));
        return elements.some((element) =>
          /bedeutungen:/i.test(element.textContent)
        );
      });
    }
  } catch (e) {
    console.log(`Error: ${e}`);
    return [];
  }
  let foundDefinitions: string[] = [];
  //await page.waitForTimeout(100000);
  if (language === "de") {
    foundDefinitions = await page.evaluate(() => {
      // const targetP = Array.from(document.querySelectorAll("*"))
      //   .filter((element) =>
      //     (element.innerText !== undefined) &&
      //     (element.innerText.toLowerCase() === "bedeutungen:") &&
      //     (element.nextElementSibling !== undefined)
      //   )[0];
      // if (!targetP) return [];
      // let nextSibling = targetP.nextElementSibling!;
      // const texts = Array.from(nextSibling.querySelectorAll("dd")).map(
      //   (el) => el.innerText,
      // );
      const texts1 = Array.from(
        document.querySelectorAll(".dwdswb-definitionen"),
      ).map((el) => el.innerText);
      const texts2 = Array.from(
        document.querySelectorAll(".dwdswb-lesart-def"),
      ).map((el) => el.innerText);
      const texts = [...texts1, ...texts2].filter((el) =>
        !el.startsWith("Produkt von")
      );
      // removes duplicates using a Set
      const cleanedTexts = [...new Set(texts)];
      // const cleanedTexts = texts
      //   .filter((def: string) => !/\[\d+\] .+ \[\d+\]/.test(def)).map((
      //     def: string,
      //   ) => def.replace(/^\[\d+\] /, "")).map((x) => x.trim());
      //return cleanedTexts;
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

  await page.setUserAgent(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537",
  );
  await page.setViewport({ width: 1280, height: 720 });
  await page.setJavaScriptEnabled(true);

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
  const poolSize = 50;
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
    ).slice(startFrom); //.slice(0, poolSize);

  // const cleanWords = ["Nadelarbeit"];

  const wordQueue = [...cleanWords];
  console.log(`Total words: ${cleanWords.length}`);
  console.log(`Pool size: ${poolSize}`);
  const pagePool = [];
  for (let i = 0; i < poolSize; i++) {
    pagePool.push(await createNewPage(browser, true));
  }

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
  // const processWord = async (word: string, page: any) => {
  //   const definitions = await extractDefinitions(
  //     word,
  //     page,
  //     maxNumber,
  //     language,
  //   );
  //   if (definitions.length === 0) {
  //     console.log(chalk.red(`No definitions found for ${word}`));
  //   } else {
  //     console.log(
  //       chalk.green(`Found ${definitions.length} definitions for ${word}`),
  //     );
  //     definitionCount += definitions.length;
  //   }
  //
  //   for (const definition of definitions) {
  //     await writer.write(JSON.stringify(definition) + "\n");
  //   }
  //
  //   processedCount++;
  //   console.log(chalk.cyan(`Definitions: ${definitionCount}`));
  //   console.log(`Progress: ${processedCount}/${totalCount}`);
  // };
  const processWord = async (
    word: string,
    page: any,
    maxRetries = 3,
  ) => {
    //console.log(`Processing word: ${word}`);
    //word = await lemmatizeWord(word);
    //console.log(`Lemmatized word: ${word}`);
    let retries = 0;

    while (retries < maxRetries) {
      try {
        // Check if the page is closed and recreate if necessary
        if (page.isClosed()) {
          page = await createNewPage(browser, false);
        }

        const definitions = await extractDefinitions(
          word,
          page,
          maxNumber,
          language,
        );
        if (definitions.length === 0) {
          console.log(chalk.red(`No definitions found for ${word}`));
        } else {
          console.log(
            chalk.green(`Found ${definitions.length} definitions for ${word}`),
          );
          definitionCount += definitions.length;
        }

        for (const definition of definitions) {
          await writer.write(JSON.stringify(definition) + "\n");
        }

        processedCount++;
        console.log(chalk.cyan(`Definitions: ${definitionCount}`));
        console.log(`Progress: ${processedCount}/${totalCount}`);
        break;
      } catch (error) {
        if (
          error.message.endsWith(
            "Execution context was destroyed, most likely because of a navigation.",
          )
        ) {
          console.log(`Retry ${retries + 1}: ${error.message}`);
          retries++;
        } else {
          console.log(`Unhandled error: ${error.message}`);
          break;
        }
      }
    }

    if (retries === maxRetries) {
      console.log(`Max retries reached for word: ${word}`);
    }
  };

  let definitionCount = 0;
  // for (const batch of wordBatches) {
  //   const promiseList = batch.map(async (word, index) => {
  //     const page = pagePool[index];
  //     const definitions = await extractDefinitions(
  //       word,
  //       page,
  //       maxNumber,
  //       language,
  //     );
  //     if (definitions.length === 0) {
  //       console.log(chalk.red(`No definitions found for ${word}`));
  //     } else {
  //       console.log(
  //         chalk.green(`Found ${definitions.length} definitions for ${word}`),
  //       );
  //       definitionCount += definitions.length;
  //     }
  //     for (const definition of definitions) {
  //       await writer.write(JSON.stringify(definition) + "\n");
  //     }
  //     processedCount++;
  //     console.log(chalk.cyan(`Definitions: ${definitionCount}`));
  //     console.log(`Progress: ${processedCount}/${totalCount}`);
  //   });
  //   await Promise.all(promiseList);
  //   writer.flush();
  // }
  // Initialize the pool and queue with first batch of promises
  const activePromises = [];
  for (let i = 0; i < poolSize && wordQueue.length > 0; i++) {
    const word = wordQueue.shift()!;
    activePromises.push(processWord(word, pagePool[i]));
  }

  // Process the rest of the queue
  while (wordQueue.length > 0 || activePromises.length > 0) {
    const finishedIndex = await Promise.race(
      activePromises.map((p, index) => p.then(() => index)),
    );

    activePromises.splice(finishedIndex, 1);

    if (wordQueue.length > 0) {
      const nextWord = wordQueue.shift()!;
      const newPromise = processWord(nextWord, pagePool[finishedIndex]);
      activePromises.push(newPromise);
    }
  }

  for (const page of pagePool) {
    await page.close();
  }

  await browser.close();
};

await main(
  10,
  "de",
  //160000,
);
