const Controller = require('./Controller.js');
const CategoriaService = require('../service/CategoriaService.js');
const converteIds = require('../utils/conversorDeStringHelper.js');


const cetegoriaService = new CategoriaService();

class CategoriaController extends Controller{
    constructor(){
        super(cetegoriaService);
    }

    async pegaAlimentos(req, res){
        const {categoria_id} = req.params;
        try{
            const alimentos = await cetegoriaService.pegaAlimentosPorCategoria(Number(categoria_id));
            return res.status(200).json({Alimentos: alimentos});
        }catch(err){
            console.log(err);
            res.status(500).send({erro: 'Erro ao buscar alimentos'});
        }
    }
}

module.exports = CategoriaController;