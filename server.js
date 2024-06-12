import Fastify from "fastify";
import fastifyCors from "@fastify/cors";
import {saveTiktok} from "./controller.js";
import fastifyStatic from "@fastify/static";
import path from "path"
import {fileURLToPath} from "url"

// Get the current directory name
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const fastify = Fastify({trustProxy: true});

fastify.register(fastifyCors, {
		origin: "*",
});


fastify.register(fastifyStatic, {
		root: path.join(__dirname, 'downloads'),
		prefix: '/', // optional: default '/'
})

fastify.post("/api/v", async (req, rep) => {
		let videoUrl = req.body.videoUrl;
		let [name, err] = await saveTiktok(videoUrl);
		if (err) {
				console.error(err);
				return rep.send({ok: false})
		}
		return rep.send({ok: true, url: name})
})


const port = process.env.PORT || 3000;
fastify.listen({port}, (err, address) => {
		if (err) {
				console.error(err);
				process.exit(1);
		}
		const msg = `Server listening on ${address}`;
		console.log(msg)
});