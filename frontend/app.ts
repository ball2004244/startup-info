import fs from "fs";
import csv from "csv-parser";

interface CSVData {
  company: string;
  date: string;
  amount: string;
  tftd: string;
  series: string;
  leadInvestor: string;
  coverage: string;
}

const readCSV = async (path: string): Promise<CSVData[]> => {
  const results: CSVData[] = [];

  return new Promise<CSVData[]>((resolve, reject) => {
    fs.createReadStream(path)
      .pipe(csv())
      .on("data", (data: CSVData) => results.push(data))
      .on("end", () => resolve(results))
      .on("error", (err: Error) => reject(err));
  });
};

const saveToJson = async (data: CSVData[], path: string): Promise<void> => {
  const json: string = JSON.stringify(data);

  return new Promise<void>((resolve, reject) => {
    fs.writeFile(path, json, (err: NodeJS.ErrnoException | null): void => {
      if (err) {
        console.log(err);
        reject(err);
      } else {
        resolve();
      }
    });
  });
};

const saveStartUpJsonData = async (filename: string): Promise<void> => {
  try {
    const data: CSVData[] = await readCSV(filename);
    const path: string = "data.json";
    await saveToJson(data, path);

    console.log("CSV read successfully!");
  } catch (err) {
    console.log("Some error occurred during CSV read!");
    console.log(err);
  }
};

let filename = "../final.csv";

if (!fs.existsSync(filename)) {
  console.log('Data file not found, loading backup data...');
  filename = "../backup/final.csv";
}
saveStartUpJsonData(filename);
