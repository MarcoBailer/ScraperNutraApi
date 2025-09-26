const { Router } = require('express'); 
const CategoriaController = require('../controller/CategoriaController.js');
const AlimentoController = require('../controller/AlimentoController.js');

const categoriaController = new CategoriaController();
const alimentoController = new AlimentoController();

const router = Router();

router.get('/categorias', (req, res) => categoriaController.getAll(req, res));
router.get('/categorias/:id', (req, res) => categoriaController.getById(req, res));
router.post('/categorias', (req, res) => categoriaController.create(req, res));
router.post('/categorias/many', (req, res) => categoriaController.createMany(req, res));
router.put('/categorias/:id', (req, res) => categoriaController.update(req, res));
router.delete('/categorias/:id', (req, res) => categoriaController.delete(req, res));
router.post('/categorias/:categoria_id/alimentos', (req, res) => alimentoController.create(req, res));
router.get('/categorias/:categoria_id/alimentos', (req, res) => categoriaController.pegaAlimentos(req, res));

module.exports = router;