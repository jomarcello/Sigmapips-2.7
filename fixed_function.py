async def _get_signal_related_trades(self, signal_id):
    """Retrieve related trades from the database"""
    try:
        # Fetch the related trades data from the database
        trades_data = await self.db.get_related_trades(signal_id)
        
        if trades_data:
            return trades_data
        else:
            logger.warning(f"No related trades data found for signal ID {signal_id}")
            return None
    except Exception as e:
        logger.error(f"Error retrieving related trades: {str(e)}")
        logger.exception(e)
        return None 