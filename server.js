import Fastify from "fastify";
import "dotenv/config"


import fastifyCors from "@fastify/cors";
import {saveTiktok} from "./controller.js";
import fastifyStatic from "@fastify/static";
import path from "path"
import {fileURLToPath} from "url"
import {addVideoView, getAuth, getVideoCount} from "./db.js";
import fastifyView from "@fastify/view";

import ejs from "ejs";
// Get the current directory name
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const fastify = Fastify({trustProxy: true});


fastify.register(fastifyView, {
		engine: {
				ejs: ejs
		},
		root: "views"
})

fastify.register(fastifyCors, {
		origin: "*",
});


fastify.register(fastifyStatic, {
		root: path.join(__dirname, 'downloads'),
		prefix: '/', // optional: default '/'
})

fastify.get("/v/:videoId", async (req, reply) => {
		await addVideoView(req.params.videoId)
		let video_count = await getVideoCount(req.params.videoId)
		return reply.viewAsync("video.ejs", {videoId: req.params.videoId, video_count});
})


fastify.post("/api/v", async (req, rep) => {
	try {
		console.log(req.headers)
		const api_key = req.headers.apikey || req.headers.auth || req.query.apikey;
		if (!api_key) {
			return rep.send({ ok: false, message: "no api key found." });
		}
		const db_api_key = await getAuth(api_key);
		const videoUrl = req.body.videoUrl;
		const name = await saveTiktok(videoUrl, db_api_key);

		return rep.send({ ok: true, url: name });
	} catch (e) {
		console.error(e);
		return rep.send({ ok: false, message: e.message });
	}
});

const port = process.env.PORT || 3000;
fastify.listen({host: "0.0.0.0", port}, (err, address) => {
		if (err) {
				console.error(err);
				process.exit(1);
		}
		const msg = `Server listening on ${address}`;
		console.log(msg)
});