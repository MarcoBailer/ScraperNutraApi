const Services = require('./Service.js')

class CategoriaService extends Services {
    constructor(){
        super('Categoria')
    }

    async pegaAlimentosPorCategoria(id){
        const categoria = await super.getByIdService(id);
        const alimentos = await categoria.getAlimentosRelacionados();
        return alimentos;
    }
}

module.exports = CategoriaService;