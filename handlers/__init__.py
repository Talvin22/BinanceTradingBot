"""Handlers package initialization"""
from aiogram import Router

# Create the main router
router = Router()

# Import routers
from .base_handlers import router as base_router
from .trading_handlers import router as trading_router

# Include routers
router.include_router(base_router)
router.include_router(trading_router)

__all__ = ['router']