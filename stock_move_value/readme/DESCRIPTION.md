This module adds value fields to the stock move model, to add visibility of how the move
has affected the stock valuation.

- **Move Value**: Value of the move including related SVL values (i.e. price differences
  and landed costs)
- **Move Origin Value**: Corresponding value of the origin move as of the the time move
  was done. Only updated for vendor returns.
- **Value Discrepancy**: Move Value + Move Origin Value. Only updated for vendor
  returns.
- **To Review**: Selected when Value Discrepancy is not zero. Users are expected to
  unselect it when review is done.
