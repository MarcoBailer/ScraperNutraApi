const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');

// Carregue os dados do arquivo JSON
const rawDataCategorias = fs.readFileSync('./arquivo_base/categorias.json');
const categoriasFormatadas = JSON.parse(rawDataCategorias);

const rawDataAlimentos = fs.readFileSync('./arquivo_base/alimentos.json');
const alimentosFormatados = JSON.parse(rawDataAlimentos);

async function createTable(db) {
  return new Promise((resolve, reject) => {
    db.run(`CREATE TABLE IF NOT EXISTS alimentos (
      id INTEGER PRIMARY KEY,
      categoria_id INTEGER,
      nome TEXT,
      grupo TEXT,
      carboidratos REAL,
      proteinas REAL,
      lipidios REAL,
      calorias REAL,
      fibra_alimentar REAL,
      vitaminas TEXT,
      minerais TEXT,
      createdAt TEXT,
      updatedAt TEXT
    )`, (err) => {
      if (err) {
        reject(err);
      } else {
        resolve();
      }
    })
    db.run(`CREATE TABLE IF NOT EXISTS categorias (
      id INTEGER PRIMARY KEY,
      nome TEXT,
      createdAt TEXT,
      updatedAt TEXT
    )`, (err) => {
      if (err) {
        reject(err);
      } else {
        resolve();
      }
    });
  });
}

async function insertData(db, stmt, data) {
  return new Promise((resolve, reject) => {
    db.run(stmt, data, (err) => {
      if (err) {
        reject(err);
      } else {
        resolve();
      }
    });
  });
}

async function importData() {
  const db = new sqlite3.Database('./src/database/storage/database.sqlite');

  try {
    await createTable(db);

    const stmtCategoria = 'INSERT INTO categorias (nome, createdAt, updatedAt) VALUES (?, ?, ?)';
    for (const categoria of categoriasFormatadas) {
      await insertData(db, stmtCategoria, [categoria.nome, categoria.createdAt, categoria.updatedAt]);
    }

    const stmtAlimento = 'INSERT INTO alimentos (categoria_id, nome, grupo, carboidratos, proteinas, lipidios, calorias, fibra_alimentar, vitaminas, minerais, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)';
    for (const alimento of alimentosFormatados) {
      await insertData(db, stmtAlimento, [alimento.categoria_id, alimento.nome, alimento.grupo, alimento.carboidratos, alimento.proteinas, alimento.lipidios, alimento.calorias, alimento.fibra_alimentar, alimento.vitaminas, alimento.minerais, alimento.createdAt, alimento.updatedAt]);
    }
  } catch (err) {
    console.error(err);
  } finally {
    db.close();
  }
}

importData();


