const express = require('express');
const alimentos = require('./AlimentosRoute.js');
const categorias = require('./CategoriaRoute.js');

module.exports = app => {
    app.use(
        express.json(), 
        alimentos,
        categorias
    );
};