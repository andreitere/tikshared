import pg from 'pg';

const {Pool} = pg;


const db = new Pool({
		host: process.env.DB_HOST,
		user: process.env.DB_USER,
		password: process.env.DB_PASS,
		database: process.env.DB_NAME,
		max: 20,
		ssl: true,
		idleTimeoutMillis: 30000,
		connectionTimeoutMillis: 2000,
})

export const getAuth = async (apiKey) => {
		let {rows} = await db.query(`select * from tikshared.api_keys where api_key = $1`, [apiKey]);
		let db_key = rows.length ? rows[0] : null;
		if (!db_key) throw new Error("No API key found.");
		return db_key;
}

export const saveVideo = async (api_key_id, url, name) => {
		await db.query(`insert into tikshared.videos (api_key_id, url, name) values ($1,$2,$3)`, [api_key_id, url, name]);
}

export const getIfSaved = async (url) => {
		let {rows} = await db.query(`select name from tikshared.videos where url = $1`, [url]);
		if (rows.length) {
				return rows[0].name
		}
		return false;
}

export const addVideoView = async (name) => {
		await db.query(`insert into tikshared.views (name) values ($1)`, [name])
}

export const getVideoCount = async (name) => {
		let {rows} = await db.query(`select count(*) as count from tikshared.views where name = $1`, [name])
		if (rows.length) {
				return rows[0].count
		}
		return 0;
}