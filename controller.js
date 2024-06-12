import {TTScraper} from "tiktok-scraper-ts";
import * as https from "https";
import * as fs from "fs";
import axios from "axios";

const TikTokScraper = new TTScraper();

export const saveTiktok = async (videoUrl) => {
		try {
				const name = Date.now();
				let res = await TikTokScraper.noWaterMark(videoUrl)
				console.log(res)
				const dest = `./downloads/${name}.mp4`
				const file = fs.createWriteStream(dest);
				await new Promise((resolve, reject) => {
						axios({
								method: "get",
								url: res,
								responseType: "stream"
						}).then(response => {
								response.data.pipe(file);
								file.on("finish", () => {
										file.close();
										console.log("Download Completed");
										return resolve()
								});
								file.on("error", (err) => {
										console.error(err)
										fs.unlinkSync(dest)
										return reject(err);
								})
						})
				})
				return [`${name}.mp4`, null]
		} catch (e) {
				return [null, e]
		}
}

