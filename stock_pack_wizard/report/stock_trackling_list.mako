<html>
<head>
    <style type="text/css">
        ${css}
        table{
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:1px solid  black;
        	border-bottom:1px solid  black;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all; 
        }
        .table_no_border{
        	border-left:none;
        	border-right:none;
        	border-top:none;
        	border-bottom:none;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
        }
       
        
        .table_horizontal_border{
        	frame:"vsides";
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:none;
        	border-bottom:none;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
        	
        }
        .table_top_border{
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:1px solid  black;
        	border-bottom:'none';
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
        }
		td{
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:1px solid  black;
        	border-bottom:1px solid  black;
         	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
		}
		th{
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:1px solid  black;
        	border-bottom:1px solid  black;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
		}
		tr{
        	border-left:1px solid  black;
        	border-right:1px solid  black;
        	border-top:1px solid  black;
        	border-bottom:1px solid  black;
        	border-collapse:collapse;
        	cellpadding:"0"; 
        	cellspacing:"0";
        	word-break:break-all;
		}

		.leftTdf{border-left:0px solid black;}  
		.topTdf{border-top:0px solid black;}  
		.rightTdf{border-right:0px solid black;}  
		.bottomTdf{border-bottom:0px solid black;} 
		.tbintb{
			border:1
			border-style: dotted
		}
    </style>
    

</head>
<body>

<% 
sum_pack=0
sum_qty=0
sum_nw=0
sum_gw=0
sum_cbm=0

cols=[
	{'width':"10%",'title':'PACK'},
	{'width':"40%",'title':'',
		'childs':[
			{'width':"30%",'title':'DESCRIPTION '},
			{'width':"10%",'title':'&nbsp;&nbsp;&nbsp;UNIT&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;PER&nbsp;&nbsp;&nbsp;PACK'},
		],  
	},
	{'width':"10%",'title':'TOTAL QTY'},
	{'width':"9%",'title':'&nbsp;&nbsp;&nbsp;N.W.&nbsp;&nbsp;&nbsp;&nbsp;(kg)'},
	{'width':"9%",'title':'&nbsp;&nbsp;&nbsp;G.W.&nbsp;&nbsp;&nbsp;&nbsp;(kg)'},
	{'width':"14%",'title':'MEASUREMENT (cm)'},
	{'width':"8%",'title':'CBM'},
]
	
%>


</br>

<table border="0"   width="100%">
	<tr>
		%for i in cols :
			<th  border="0" width=${i['width']} height=50 >
				${i['title']}
				%if i.get('childs'):
					<table border="0"  >
						<tr>
							%for child in i['childs']:
								<th width=${child['width']}  >${child['title']}</th>
							%endfor
						</tr>
					</table>
				%endif
			</th>
		%endfor
	</tr>
</table>


<table  border="1"   width="100%" class=table_horizontal_border >
	%for tracking in objects :
		<tr>
			<td width="10%" vAlign="top">${tracking.name}</td>
			<td width="40%">
				<table  border="1" class=table_top_border >
					<tr height="20" class=table_top_border>
							<td align="left" ></td>
							<td align="left"></td>
					</tr>
					%for i  in range(len(tracking.move_ids)):
						<% move= tracking.move_ids[i] %>
						<tr>
							<td width="30%" align="left">${get_description(move.product_id.id)}</td>
							<td width="10%"   valign="top" align="center">${move.product_qty}</td>
							<%sum_qty += move.product_qty %>
						</tr>
					%endfor
				</table>
			</td>
			
			<td width="10%" valign="top" align="center">${get_total_qty( tracking.id )} </td>
			<td width="9%" valign="top" align="center">${tracking.net_weight}</td>
			<td width="9%" valign="top" align="center">${tracking.gross_weight}</td>
			<td width="14%" valign="top" align="center">${get_measurement( tracking.id )}</td> 
			<td width="8%" valign="top" align="center" >${tracking.pack_cbm } </td>  
			
			<% 
				sum_nw+=tracking.net_weight
				sum_gw+=tracking.gross_weight
				sum_cbm+=tracking.pack_cbm  
				sum_pack+=1
			%>
		</tr>
	%endfor
</table>

<p class=title>TOTAL:</p>

<table border="1"  width="100%" class=table_horizontal_border>
	<tr>
		<th width=${cols[0]['width']}  >${sum_pack}</th>
		<th width=${cols[1]['width']}  >  </th>
		<th width=${cols[2]['width']}  >${sum_qty}</th>
		<th width=${cols[3]['width']} style="mso-number-format:'0\.000';" >${sum_nw}</th>
		<th width=${cols[4]['width']} style="mso-number-format:'0\.000';" >${sum_gw}</th>
		<th width=${cols[5]['width']}  >  </th>
		<th width=${cols[6]['width']}  >${sum_cbm}</th>
	</tr>
</table>







</body>
</html>




<%doc>

	{'width':"10%",'title':'PACK'},
	{'width':"40%",'title':' ',
		'childs':[
			{'width':"30%",'title':'DESCRIPTION'},
			{'width':"10%",'title':'UNIT PER PACK'},
		],  
	},
	{'width':"10%",'title':'N.W. (kg)'},
	{'width':"10%",'title':'G.W. (kg)'},
	{'width':"10%",'title':'MEASUREMENT'},
	{'width':"10%",'title':'TOTAL QTY'},
	{'width':"10%",'title':'CBM'},

<div class="footer">
	${time.strftime('%Y-%m-%d %H:%M:%S')}
	<p>${company.partner_id.name}</p>
</div>


<img src="data:image/png;base64,${company.logo}"  class="header"/>
<hr class="underline" width='100%'/>


<p>${company.partner_id.name}</p>

<p>${display_address(company.partner_id)}</p>

%if company.partner_id.phone:
<p>Phone:  ${company.partner_id.phone}</p>
%endif 
%if company.partner_id.phone:
<p>E-mail:  ${company.partner_id.email}</p>
%endif 


<hr class="underline" width="27%" />

<br/>
            
</%doc>





