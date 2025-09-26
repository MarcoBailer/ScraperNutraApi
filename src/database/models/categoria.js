'use strict';
const {
  Model
} = require('sequelize');
module.exports = (sequelize, DataTypes) => {
  class Categoria extends Model {
    static associate(models) {
      Categoria.hasMany(models.Alimento, {
        foreignKey: 'categoria_id',
        as: 'alimentosRelacionados'
      });
    }
  }
  Categoria.init({
    nome: DataTypes.STRING
  }, {
    sequelize,
    modelName: 'Categoria',
    tableName: 'categorias',
    paranoid: true,
  });
  return Categoria;
};