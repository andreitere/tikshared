import {TTScraper} from "tiktok-scraper-ts";
import * as https from "https";
import * as fs from "fs";
import axios from "axios";
import {v4 as uuidv4} from "uuid"
import {getIfSaved, saveVideo} from "./db.js";

const TikTokScraper = new TTScraper();


export const saveTiktok = async (videoUrl, db_api_key) => {
		let existing = await getIfSaved(videoUrl);
		if (existing) {
				return `${existing}`;
		}
		const name = uuidv4()
		let res = await TikTokScraper.noWaterMark(videoUrl)
		const dest = `./downloads/${name}.mp4`
		const file = fs.createWriteStream(dest);
		await new Promise((resolve, reject) => {
				axios({
						method: "get", url: res, responseType: "stream"
				}).then(response => {
						response.data.pipe(file);
						file.on("finish", () => {
								file.close();
								return resolve()
						});
						file.on("error", (err) => {
								console.error(err)
								fs.unlinkSync(dest)
								return reject(err);
						})
				})
		})
		await saveVideo(db_api_key.id, videoUrl, name)
		return `${name}`
}

