'use strict';
const notNegative = require('../../utils/notNegativaHelper.js')

const {
  Model
} = require('sequelize');
module.exports = (sequelize, DataTypes) => {
  class Alimento extends Model {
    static associate(models) {
      Alimento.belongsTo(models.Categoria, {
        foreignKey: 'categoria_id'
      })
    }
  }
  Alimento.init({
    grupo: {
      type: DataTypes.STRING,
      unique: {
        args: true,
        msg: 'O grupo do alimento já está cadastrado'
      },
      validate: {
        notEmpty: {
          args: true,
          msg: 'O campo grupo não pode ser vazio'
        }
      }
    },
    nome: {
      type : DataTypes.STRING,
      unique: {
        args: true,
        msg: 'O nome do alimento já está cadastrado'
      },
      validate:
      {
        notEmpty: {
          args: true, 
          msg: 'O campo nome não pode ser vazio'
        }
      }
    },
    carboidratos: {
      type: DataTypes.DOUBLE,
      allowNull: false,
      validate: {
        notNull: {
          args: true,
          msg: 'O campo carboidratos não pode ser nulo'
        },
        isNumeric: {
          args: true,
          msg: 'O campo carboidratos deve ser numérico'
        },
        notNegative: (valor) => {
          if (valor < 0) {
            throw new Error('O campo carboidratos não pode ser negativo')
          }
        }
      }
    },
    proteinas: {
      type: DataTypes.DOUBLE,
      allowNull: false,
      validate: {
        notNull: {
          args: true,
          msg: 'O campo proteínas não pode ser nulo'
        },
        isNumeric: {
          args: true,
          msg: 'O campo proteínas deve ser numérico'
        },
        notNegative: (valor) => {
          if (valor < 0) {
            throw new Error('O campo proteinas não pode ser negativo')
          }
        }
      }
    },
    lipidios: {
      type: DataTypes.DOUBLE,
      allowNull: false,
      validate: {
        notNull: {
          args: true,
          msg: 'O campo lipídios não pode ser nulo'
        },
        isNumeric: {
          args: true,
          msg: 'O campo lipídios deve ser numérico'
        },
        notNegative: (valor) => {
          if (valor < 0) {
            throw new Error('O campo lipidios não pode ser negativo')
          }
        }
      }
    },
    calorias: {
      type: DataTypes.DOUBLE,
      allowNull: false,
      validate: {
        notNull: {
          args: true,
          msg: 'O campo calorias não pode ser nulo'
        },
        isNumeric: {
          args: true,
          msg: 'O campo calorias deve ser numérico'
        },
        notNegative: (valor) => {
          if (valor < 0) {
            throw new Error('O campo calorias não pode ser negativo')
          }
        }
      }
    },
    vitaminas: {
      type: DataTypes.STRING,
      validate: {
        notEmpty: {
          args: true,
          msg: 'O campo vitaminas não pode ser vazio'
        }
      },
    },
    minerais: {
      type: DataTypes.STRING,
      validate: {
        notEmpty: {
          args: true,
          msg: 'O campo minerais não pode ser vazio'
        }
      },
    },
    fibra_alimentar: {
      type: DataTypes.DOUBLE,
      allowNull: false,
      validate: {
        notNull: {
          args: true,
          msg: 'O campo fibra alimentar não pode ser nulo'
        },
        isNumeric: {
          args: true,
          msg: 'O campo fibra alimentar deve ser numérico'
        },
        notNegative: (valor) => {
          if (valor < 0) {
            throw new Error('O campo fibra alimentar não pode ser negativo')
          }
        }
      }
    },
  }, {
    sequelize,
    modelName: 'Alimento',
    tableName: 'alimentos',
    paranoid: true,
  });
  return Alimento;
};