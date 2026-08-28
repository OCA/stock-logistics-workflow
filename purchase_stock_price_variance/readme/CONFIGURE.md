1. Navigate to *Inventory > Configuration > Settings*.
2. Find and enable the 'Enable Price Variance Error' option to activate this feature.
   An error will occur if the price difference exceeds the threshold when receiving the product.
3. Set the following global values to apply if no specific value is set at the product level.
    If the threshold value is set to 0, this threshold will not be checked.
    * **Price Variance Threshold Percent**: Default percentage variance for all products.
    * **Price Variance Threshold Amount**: Default maximum variance for all products.
4. Go to *Inventory > Configuration > Product Categories*.
5. Enable **Bypass Price Variance Check** to skip the error check for the products under this category.
6. Go to *Inventory > Products* and open the product.
7. Click on the Inventory tab and configure the following fields.
    If the threshold value is set to 0, the threshold will refer to the global value.
    * **Bypass Price Variance Check**: Enable this to skip the error check for this specific product.
    * **Price Variance Threshold Percent**: Set the allowable percentage variance.
    * **Price Variance Threshold Amount**: Define the maximum allowable price variance.
8. Assign the internal user to the "Manage Price Variance Check" group. 
   This will make the "Bypass Price Variance Check" checkbox updatable in the receipt form.
