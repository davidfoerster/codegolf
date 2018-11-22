#include<stdlib.h>
#include<stdio.h>
blow_up_golfed1(char*s)
{
	char*S=s;
	while(*S++);
	const int l=S-s-1;
	int i=1,j=0,k,d,o,t[l*3],*v;
	for(;i<l;i++)(d=s[i]+~(t[j++]=s[i-1]))>0&&(t[j++]=-d,d%2||(t[j++]=0));
	l>0&&(t[j++]=s[l-1]);
	v=calloc(k=j,4);
	for(i=0;i<k;i++) {
		if((d=-t[i])>0) {
			d+=o=d%2;
			for(j=0;j<d&&j<=i;j++)v[i-j]+=d-j;
			i+=!o;
			for(j=o;j<d&&i+j<k;j++)v[i+j]+=d-j;
		}
	}
	for(i=0;i<k;i++) {
		d=v[i];printf(d?"%d":"%c",d?d:t[i]);
	}
}
