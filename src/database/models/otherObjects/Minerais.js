//Criar classe generica para transformar os dados de vitaminas em um objeto

class Minerais {
    constructor(nome, quantidade) {
        this.nome = nome;
        this.quantidade = quantidade;
    }

    static parseMineraisString(mineraisString) {
        const MineraisArray = mineraisString.split(',').map(item => item.trim());
        const result = {};

        MineraisArray.forEach(item => {
            const [nome, quantidade] = item.split(':').map(part => part.trim());
            result[nome] = parseFloat(quantidade);
        });

        return result;
    }
}

module.exports = Minerais;
