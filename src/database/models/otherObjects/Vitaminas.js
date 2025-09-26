//Criar classe generica para transformar os dados de vitaminas em um objeto

class Vitaminas {
    constructor(nome, quantidade) {
        this.nome = nome;
        this.quantidade = quantidade;
    }

    static parseVitaminasString(vitaminasString) {
        const vitaminasArray = vitaminasString.split(',').map(item => item.trim());
        const result = {};

        vitaminasArray.forEach(item => {
            const [nome, quantidade] = item.split(':').map(part => part.trim());
            result[nome] = parseFloat(quantidade);
        });

        return result;
    }
}

module.exports = Vitaminas;
